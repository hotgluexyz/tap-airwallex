"""REST client handling, including airwallexStream base class."""

from types import prepare_class
import requests
from pathlib import Path
from typing import Any, Dict, Optional, Union, List, Iterable

from memoization import cached

from hotglue_singer_sdk.helpers.jsonpath import extract_jsonpath
from hotglue_singer_sdk.streams import RESTStream

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
        params["page_size"] = 100
        if next_page_token:
            params["page_num"] = next_page_token
        if self.replication_key and self.replication_key_filter_field:
            start_date = self.get_starting_time(context)
            params[self.replication_key_filter_field] = start_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        return params


    # def parse_response(self, response: requests.Response) -> Iterable[dict]:
    #     """Parse the response and return an iterator of result rows."""
    #     # TODO: Parse response body and return a set of records.
    #     yield from extract_jsonpath(self.records_jsonpath, input=response.json())

