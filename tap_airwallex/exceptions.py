"""Airwallex-specific exceptions."""

import requests

# Airwallex returns 401 for both bad credentials and insufficient scope,
#   bad key gives {"code": "credentials_invalid", "message": "UNAUTHORIZED"}
#   bad scope gives {"code": "unauthorized", "message": "Insufficient permissions"}
PERMISSION_ERROR_HINTS = ("permission", "scope")


class InsufficientPermissionsError(Exception):
    """Raised when credentials are valid but lack the required permission scope."""


def is_permission_error(response: requests.Response) -> bool:
    try:
        body = response.json()
    except ValueError:
        return False
    if not isinstance(body, dict):
        return False
    text = " ".join(
        str(body.get(field, "")) for field in ("code", "message")
    ).lower()
    return any(hint in text for hint in PERMISSION_ERROR_HINTS)
