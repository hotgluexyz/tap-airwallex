"""airwallex Authentication."""


from hotglue_singer_sdk.authenticators import OAuthAuthenticator
from hotglue_singer_sdk.authenticators import SingletonMeta
from pendulum import parse
from datetime import datetime
import json
from hotglue_etl_exceptions import InvalidCredentialsError
import requests

class AirwallexAuthenticator(OAuthAuthenticator, metaclass=SingletonMeta):
    """Authenticator class for airwallex."""

    def __init__(self, stream, auth_endpoint=None, oauth_scopes=None, default_expiration=None, config_file=None):
        super().__init__(
            stream=stream,
            auth_endpoint=auth_endpoint,
            oauth_scopes=oauth_scopes,
            default_expiration=default_expiration,
            config_file=config_file,
        )
        self.account_id = None
        self._token_account_id = None

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
            self.logger.info(f"Updating token due to account ID mismatch: {self.account_id} != {self._token_account_id}")
            self._token_account_id = self.account_id
            self.logger.info(f"Updated token account ID to: {self._token_account_id}")
            return False
        if permission_type == "organization" and self._token_account_id is not None:
            self._token_account_id = None
            return False
        # if expires_in is not set, try to get it from the tap config
        if self.expires_in is None and self._tap.config.get("expires_at"):
            self.expires_in = self._tap.config.get("expires_at")
            self.expires_in = parse(self.expires_in).timestamp()
        if not self.expires_in:
            return False
        if int(self.expires_in) - int(datetime.utcnow().timestamp()) > 120:
            return True
        return False

    def update_access_token_locally(self) -> None:
        """Update `access_token` locally."""

        token_response = requests.post(self.auth_endpoint, headers=self.oauth_request_headers)
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
        self._token_account_id = self.account_id

        # Update the tap config with the new access_token and refresh_token
        self._tap._config["access_token"] = token_json["token"]
        self._tap._config["expires_in"] = self.expires_in

        # Write the updated config back to the file (only when config was loaded from a path)
        if self._tap.config_file is not None:
            with open(self._tap.config_file, "w") as outfile:
                json.dump(self._tap._config, outfile, indent=4)

    @classmethod
    def create_for_stream(cls, stream) -> "AirwallexAuthenticator":
        auth_endpoint = stream.url_base + "/authentication/login"
        return cls(
            stream=stream,
            auth_endpoint=auth_endpoint,
            oauth_scopes="TODO: OAuth Scopes",
        )
