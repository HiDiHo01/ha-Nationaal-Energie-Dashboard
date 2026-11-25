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
from .quarter import NedPowerDataset, NedPowerReading, NedQuarterClient
from .rate_limiter import NedRequestBudget
from .transport import NedTransport, TransportResponse

__all__ = [
    "NedAccessDeniedError",
    "NedApiError",
    "NedAuthenticationClient",
    "NedAuthenticationError",
    "NedConnectionError",
    "NedPermissionError",
    "NedPowerDataset",
    "NedPowerReading",
    "NedQuarterClient",
    "NedRateLimitError",
    "NedRequestBudget",
    "NedResponseError",
    "NedTimeoutError",
    "NedTransport",
    "NedUnsupportedDatasetError",
    "NedValidationError",
    "TransportResponse",
]
