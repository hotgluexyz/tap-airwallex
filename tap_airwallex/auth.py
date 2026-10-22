"""airwallex Authentication."""


import hashlib
import json
from datetime import datetime, timezone

from hotglue_singer_sdk.authenticators import OAuthAuthenticator
from hotglue_singer_sdk.authenticators import SingletonMeta
from hotglue_etl_exceptions import InvalidCredentialsError
from pendulum import parse
import requests


def get_login_endpoint(is_sandbox: bool) -> str:
    """Return the Airwallex login endpoint for the configured environment."""
    api_host = "https://api-demo.airwallex.com" if is_sandbox else "https://api.airwallex.com"
    return f"{api_host}/api/v1/authentication/login"


class AirwallexOAuthAuthenticator(OAuthAuthenticator):
    """Connector-bound authenticator for Airwallex OAuth access tokens."""

    def __init__(self, stream, auth_endpoint=None, oauth_scopes=None, default_expiration=None, config_file=None):
        super().__init__(
            stream=stream,
            auth_endpoint=auth_endpoint,
            oauth_scopes=oauth_scopes,
            default_expiration=default_expiration,
            config_file=config_file,
        )
        self._stream = stream
        self.account_id = None
        self._token_account_id = None

    def _token_context(self) -> dict:
        return {
            "is_sandbox": bool(self.config.get("is_sandbox", False)),
            "client_id": self.config["client_id"],
            "api_key_sha256": hashlib.sha256(
                self.config["api_key"].encode()
            ).hexdigest(),
        }

    @property
    def oauth_request_headers(self) -> str:
        """Return the authentication endpoint."""
        payload = {
            "Content-Type": "application/json",
            "x-api-key": self.config["api_key"],
            "x-client-id": self.config["client_id"]
        }
        if getattr(self._stream, "permission_type", None) == "account" and self.account_id:
            self.logger.info(f"Logging in as account: {self.account_id}")
            payload["x-login-as"] = self.account_id
        return payload

    def is_token_valid(self) -> bool:
        """Check if token is valid.

        Returns:
            True if the token is valid (fresh).
        """
        permission_type = getattr(self._stream, "permission_type", None)
        if permission_type == "account" and not self.account_id:
            raise InvalidCredentialsError(f"Account ID is required for stream: {self._stream.name} because permission type is account")
        if permission_type == "account" and self.account_id != self._token_account_id:
            return False
        if permission_type == "organization" and self._token_account_id is not None:
            return False
        if self.expires_in is None:
            token_context_matches = (
                self._tap.config.get("_access_token_context")
                == self._token_context()
            )
            if (
                token_context_matches
                and self._tap.config.get("access_token")
                and self._tap.config.get("expires_in")
            ):
                self.access_token = self._tap.config["access_token"]
                self.expires_in = self._tap.config["expires_in"]
            elif token_context_matches and self._tap.config.get("expires_at"):
                self.expires_in = parse(self._tap.config["expires_at"]).timestamp()
        if not self.expires_in:
            return False
        if int(self.expires_in) - int(datetime.now(timezone.utc).timestamp()) > 120:
            return True
        return False

    def update_access_token_locally(self) -> None:
        """Update `access_token` locally."""
        # add account_id as _token_account_id before make the request
        self._token_account_id = self.account_id

        try:
            token_response = requests.post(
                self.auth_endpoint,
                headers=self.oauth_request_headers,
                timeout=30,
            )
        except requests.exceptions.RequestException as ex:
            raise InvalidCredentialsError(f"Failed OAuth login: {ex}") from ex
        try:
            token_response.raise_for_status()
            self.logger.info("OAuth authorization attempt was successful.")
        except Exception as ex:
            raise InvalidCredentialsError(
                f"Failed OAuth login, response was '{token_response.text}'. {ex}"
            )
        token_json = token_response.json()
        self.access_token = token_json["token"]
        expires_in = token_json.get("expires_at")
        self.expires_in = parse(expires_in).timestamp()

        # Update the tap config with the new access_token and refresh_token
        self._tap._config["access_token"] = token_json["token"]
        self._tap._config["expires_in"] = self.expires_in
        self._tap._config["_access_token_context"] = self._token_context()

        # Write the updated config back to the file (only when config was loaded from a path)
        if self._tap.config_file is not None:
            with open(self._tap.config_file, "w") as outfile:
                json.dump(self._tap._config, outfile, indent=4)

class AirwallexAuthenticator(AirwallexOAuthAuthenticator, metaclass=SingletonMeta):
    """Singleton authenticator used by normal stream syncs."""

    @classmethod
    def create_for_stream(cls, stream) -> "AirwallexAuthenticator":
        auth_endpoint = get_login_endpoint(stream.config.get("is_sandbox", False))
        return cls(
            stream=stream,
            auth_endpoint=auth_endpoint,
            oauth_scopes="TODO: OAuth Scopes",
        )
