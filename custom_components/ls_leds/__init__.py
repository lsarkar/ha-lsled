from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

import logging

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config: ConfigEntry):
    platforms = ["light"]
    await hass.config_entries.async_forward_entry_setups(config, platforms)
    return True
