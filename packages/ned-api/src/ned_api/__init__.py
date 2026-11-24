"""Provide the independent Nationaal Energie Dashboard API library."""

from .exceptions import (
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

__all__ = [
    "NedApiError",
    "NedAuthenticationError",
    "NedConnectionError",
    "NedPermissionError",
    "NedRateLimitError",
    "NedResponseError",
    "NedTimeoutError",
    "NedUnsupportedDatasetError",
    "NedValidationError",
]
