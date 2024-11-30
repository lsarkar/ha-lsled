from .config_flow import LSLightsConfigFlow
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .light import LightEntity, LightStrip, Ws281XLedStrip

import logging

"""
async def async_setup(hass, config):
    #Set up the integration
    return True
"""

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config: ConfigEntry):
    await hass.config_entries.async_forward_entry_setup(config, "light")
    return True
