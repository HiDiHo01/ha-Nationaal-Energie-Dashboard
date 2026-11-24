"""Define contract-independent errors for the NED API library."""


class NedApiError(Exception):
    """Base error for NED operations; messages must not contain credentials."""


class NedAuthenticationError(NedApiError):
    """Indicate a confirmed authentication failure."""


class NedPermissionError(NedApiError):
    """Indicate insufficient permission for an operation."""


class NedConnectionError(NedApiError):
    """Indicate a transport connection failure."""


class NedTimeoutError(NedApiError):
    """Indicate that an operation exceeded its time budget."""


class NedRateLimitError(NedApiError):
    """Indicate that a request limit prevents an operation."""


class NedResponseError(NedApiError):
    """Indicate an unexpected or invalid response."""


class NedValidationError(NedApiError):
    """Indicate invalid input to the library."""


class NedUnsupportedDatasetError(NedApiError):
    """Indicate a dataset outside the supported catalog."""
