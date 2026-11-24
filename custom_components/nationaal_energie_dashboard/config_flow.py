"""Expose a translated, fail-closed configuration entry point."""

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult

from .const import CONTRACT_PENDING, DOMAIN


class NedConfigFlow(ConfigFlow, domain=DOMAIN):
    """Prevent configuration until the authenticated client is available."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, object] | None = None
    ) -> ConfigFlowResult:
        """Explain the contract blocker without collecting an API key."""
        return self.async_abort(reason=CONTRACT_PENDING)
