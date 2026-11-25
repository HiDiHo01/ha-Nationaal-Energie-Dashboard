"""Prepare masked credential entry and native configuration flows."""

from collections.abc import Mapping
from typing import Any, Self, override

import probatio
from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from ned_api import (
    NedAccessDeniedError,
    NedApiError,
    NedAuthenticationClient,
    NedAuthenticationError,
    NedConnectionError,
    NedRateLimitError,
    NedTimeoutError,
    NedValidationError,
    validate_key_format,
)

from .const import DOMAIN
from .coordinator import get_request_budget

API_KEY_SCHEMA = probatio.Schema(
    {probatio.Required(probatio.Secret(CONF_API_KEY)): cv.string}
)


async def async_validate_api_key(hass: HomeAssistant, api_key: str) -> None:
    """Use the real bounded positive authentication check with Core's session."""
    budget = get_request_budget(hass)
    session = async_create_clientsession(
        hass, auto_cleanup=False, middlewares=(budget.async_middleware,)
    )
    try:
        await NedAuthenticationClient(session, budget).async_validate_api_key(api_key)
    finally:
        session.detach()


class NedConfigFlow(ConfigFlow, domain=DOMAIN):
    """Collect a masked API key and preserve one config entry per service."""

    VERSION = 1

    @override
    def is_matching(self, other_flow: Self) -> bool:
        """Match only flows with the same established service identity."""
        return self.unique_id is not None and self.unique_id == other_flow.unique_id

    @override
    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Start the single-service configuration flow."""
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()
        self._async_abort_entries_match()
        return await self._async_key_step("user", user_input)

    async def async_step_reauth(
        self, _entry_data: Mapping[str, Any]
    ) -> ConfigFlowResult:
        """Request a replacement key without pre-filling the existing key."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Validate replacement credentials for the existing entry."""
        return await self._async_key_step(
            "reauth_confirm", user_input, self._get_reauth_entry()
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Allow key changes without creating new entities or config entries."""
        return await self._async_key_step(
            "reconfigure", user_input, self._get_reconfigure_entry()
        )

    async def _async_key_step(
        self,
        step_id: str,
        user_input: dict[str, Any] | None,
        entry: ConfigEntry | None = None,
    ) -> ConfigFlowResult:
        """Save only authenticated credentials; never log or echo a secret."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                api_key = validate_key_format(user_input.get(CONF_API_KEY))
            except NedValidationError:
                errors[CONF_API_KEY] = "invalid_key_format"
            else:
                try:
                    await async_validate_api_key(self.hass, api_key)
                except NedAuthenticationError:
                    errors[CONF_API_KEY] = "invalid_auth"
                except NedAccessDeniedError:
                    errors["base"] = "access_denied"
                except NedConnectionError, NedTimeoutError:
                    errors["base"] = "cannot_connect"
                except NedRateLimitError:
                    errors["base"] = "rate_limited"
                except NedApiError:
                    errors["base"] = "cannot_validate"
                else:
                    if entry is not None:
                        return self.async_update_reload_and_abort(
                            entry,
                            data_updates={CONF_API_KEY: api_key},
                            reason=(
                                "reauth_successful"
                                if step_id == "reauth_confirm"
                                else "reconfigure_successful"
                            ),
                        )
                    return self.async_create_entry(
                        title="Nationaal Energie Dashboard",
                        data={CONF_API_KEY: api_key},
                    )

        return self.async_show_form(
            step_id=step_id,
            data_schema=API_KEY_SCHEMA,
            errors=errors,
        )
