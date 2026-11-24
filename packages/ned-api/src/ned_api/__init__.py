"""Provide the independent Nationaal Energie Dashboard API library."""

from .authentication import NedAuthenticationClient
from .exceptions import (
    NedAccessDeniedError,
    NedApiError,
    NedAuthenticationError,
    NedConnectionError,
    NedPermissionError,
    NedRateLimitError,
    NedResponseError,
    NedTimeoutError,
    NedUnsupportedDatasetError,
    NedValidationError,
)
from .transport import NedTransport, TransportResponse

__all__ = [
    "NedAccessDeniedError",
    "NedApiError",
    "NedAuthenticationClient",
    "NedAuthenticationError",
    "NedConnectionError",
    "NedPermissionError",
    "NedRateLimitError",
    "NedResponseError",
    "NedTimeoutError",
    "NedTransport",
    "NedUnsupportedDatasetError",
    "NedValidationError",
    "TransportResponse",
]
