"""Airwallex-specific exceptions."""


class InsufficientPermissionsError(Exception):
    """Raised when credentials are valid but lack the required permission scope."""
