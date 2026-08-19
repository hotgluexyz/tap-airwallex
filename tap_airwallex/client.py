"""REST client handling, including airwallexStream base class."""

import requests
from pathlib import Path
from typing import Any, Dict, Optional, Iterator, Tuple, Iterable
from datetime import datetime, timedelta, timezone

from memoization import cached

from hotglue_singer_sdk.streams import RESTStream
from hotglue_singer_sdk.exceptions import FatalAPIError

from tap_airwallex.auth import AirwallexAuthenticator


SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class AirwallexStream(RESTStream):
    """airwallex stream class."""

    @property
    def url_base(self) -> str:
        """Return the API URL root, configurable via tap settings."""
        if self.config.get("is_sandbox", False):
            return "https://api-demo.airwallex.com/api/v1"
        return "https://api.airwallex.com/api/v1"

    records_jsonpath = "$.items[*]"
    replication_key_filter_field = None
    pagination_page_field = "page_num"
    page_size_field = "page_size"

    @property
    @cached
    def authenticator(self) -> AirwallexAuthenticator:
        """Return a new authenticator object."""
        return AirwallexAuthenticator.create_for_stream(self)

    @property
    def http_headers(self) -> dict:
        """Return the http headers needed."""
        headers = {}
        if "user_agent" in self.config:
            headers["User-Agent"] = self.config.get("user_agent")
        headers["x-api-version"] = "2026-06-30"
        return headers

    def get_next_page_token(
        self, response: requests.Response, previous_token: Optional[Any]
    ) -> Optional[Any]:
        """Return a token for identifying next page or None if no more pages."""
        previous_token = previous_token or 0
        res_json = response.json()
        if res_json.get("has_more"):
            return previous_token + 1
        return None

    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {}
        params[self.page_size_field] = 100
        if next_page_token is not None:
            params[self.pagination_page_field] = next_page_token
        if self.replication_key and self.replication_key_filter_field:
            start_date = self.get_starting_time(context)
            params[self.replication_key_filter_field] = start_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        return params

    def validate_response(self, response: requests.Response) -> None:
        """Log Airwallex error body before raising — SDK message only includes path."""
        if 400 <= response.status_code < 500:
            self.logger.error(
                "Airwallex API error %s: url=%s body=%s",
                response.status_code,
                response.url,
                response.text,
            )
        super().validate_response(response)

    def prepare_request(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> requests.PreparedRequest:
        """Pass partition context to the shared authenticator before each request."""
        auth = self.authenticator
        if auth is not None:
            auth._stream = self
            permission_type = getattr(self, "permission_type", None)
            if permission_type == "account":
                auth.account_id = (context or {}).get("account_id")
            elif permission_type == "organization":
                auth.account_id = None
        return super().prepare_request(context, next_page_token)


class SpendStream(AirwallexStream):
    """Define spend stream."""

    def get_next_page_token(
        self, response: requests.Response, previous_token: Optional[Any]
    ) -> Optional[Any]:
        """Return a token for identifying next page or None if no more pages."""
        previous_token = previous_token or 0
        res_json = response.json()
        next_page_token = res_json.get("page_after")
        return next_page_token

    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {}
        if next_page_token:
            params["page"] = next_page_token
        # spend streams need to pass from_created_at to bypass 30 day limit
        # bills can't be updated after being approved, but status can change once bill is paid
        # so if we use from_created_at as a normal replication key the tap won't fetch status updates
        # defaulting from_created_at to 2020-01-01 to emulate a full sync
        params["from_created_at"] = "2020-01-01T00:00:00.000Z"
        return params


class DateRangeStream(AirwallexStream):
    """Define date range stream."""

    @staticmethod
    def _to_utc(dt: datetime) -> datetime:
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)

    @classmethod
    def _monthly_windows(
        cls, start: datetime, end: datetime
    ) -> Iterator[Tuple[datetime, datetime]]:
        """Yield inclusive (from_created_at, to_created_at) monthly windows."""
        start = cls._to_utc(start)
        end = cls._to_utc(end)
        cursor = start
        while cursor < end:
            year, month = cursor.year, cursor.month
            if month == 12:
                next_month = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
            else:
                next_month = datetime(year, month + 1, 1, tzinfo=timezone.utc)
            window_end = min(next_month, end)
            if window_end < end:
                # API treats both bounds as inclusive; avoid double-counting the boundary.
                yield cursor, window_end - timedelta(microseconds=1)
                cursor = next_month
            else:
                yield cursor, end
                break

    def request_records(self, context: Optional[dict]) -> Iterable[dict]:
        """Paginate within monthly date windows to stay under max page_num."""
        start = self.get_starting_time(context)
        end = datetime.now(tz=timezone.utc)
        for window_start, window_end in self._monthly_windows(start, end):
            self._window_start = window_start
            self._window_end = window_end
            self.logger.info(
                f"{self.name} window %s -> %s",
                window_start.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                window_end.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            )
            yield from super().request_records(context)

    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params = super().get_url_params(context, next_page_token)
        params["from_created_at"] = self._window_start.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        params["to_created_at"] = self._window_end.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        return params

    def get_next_page_token(
        self, response: requests.Response, previous_token: Optional[Any]
    ) -> Optional[Any]:
        """Return next page_num, or raise if the window exceeds Airwallex's max."""
        previous_token = previous_token or 0
        if not response.json().get("has_more"):
            return None
        next_token = previous_token + 1
        max_page_num = getattr(self, "max_page_num", None)
        if max_page_num is not None and next_token > max_page_num:
            raise FatalAPIError(
                f"{self.name} exceeded max page_num ({max_page_num}) "
                f"for window {self._window_start.isoformat()} -> "
                f"{self._window_end.isoformat()}; narrow the date window"
            )
        return next_token