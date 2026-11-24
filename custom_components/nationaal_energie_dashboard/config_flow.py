"""Prepare masked credential entry and native configuration flows."""

from collections.abc import Mapping
from typing import Any, override

import probatio

from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryError
from homeassistant.helpers import config_validation as cv

from .const import CONTRACT_PENDING, DOMAIN

API_KEY_SCHEMA = probatio.Schema(
    {probatio.Required(probatio.Secret(CONF_API_KEY)): cv.string}
)


async def async_validate_api_key(
    _hass: HomeAssistant, _api_key: str
) -> None:
    """Fail closed until a validated NED client can authenticate the key.

    The future client must use bounded, authenticated requests and sanitized
    exceptions. This draft neither sends the key nor treats syntax as proof
    of authentication.
    """
    raise ConfigEntryError(
        translation_domain=DOMAIN,
        translation_key=CONTRACT_PENDING,
    )


class NedConfigFlow(ConfigFlow, domain=DOMAIN):
    """Collect a masked API key and preserve one config entry per service."""

    VERSION = 1

    @override
    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Start the single-service configuration flow."""
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()
        self._async_abort_entries_match()
        return await self._async_key_step("user", user_input)

    @override
    async def async_step_reauth(
        self, entry_data: Mapping[str, Any]
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
            api_key = user_input.get(CONF_API_KEY)
            if not isinstance(api_key, str) or not api_key or any(
                char.isspace() or ord(char) < 32 or ord(char) == 127
                for char in api_key
            ):
                errors[CONF_API_KEY] = "invalid_key_format"
            else:
                try:
                    await async_validate_api_key(self.hass, api_key)
                except ConfigEntryError:
                    errors["base"] = CONTRACT_PENDING
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
