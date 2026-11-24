"""Test the public, contract-independent exception hierarchy."""

import pytest

from ned_api import (
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


@pytest.mark.parametrize(
    "error_type",
    [
        NedAuthenticationError,
        NedConnectionError,
        NedPermissionError,
        NedRateLimitError,
        NedResponseError,
        NedTimeoutError,
        NedUnsupportedDatasetError,
        NedValidationError,
    ],
)
def test_public_error_hierarchy(error_type: type[NedApiError]) -> None:
    """Catch each specific error via the public base without losing its type."""
    message = "Synthetic operation failed."
    with pytest.raises(NedApiError) as caught:
        raise error_type(message)
    assert type(caught.value) is error_type
    assert str(caught.value) == message


def test_base_error() -> None:
    """Expose a common exception base independent of Home Assistant."""
    assert issubclass(NedApiError, Exception)
