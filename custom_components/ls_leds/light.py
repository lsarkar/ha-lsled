"""Platform for light integration."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any, Dict

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.components.light import (
    ATTR_RGB_COLOR,
    PLATFORM_SCHEMA,
    ColorMode,
    LightEntity,
)
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_ON, STATE_OFF


from enum import IntEnum

from .const import DOMAIN
from .const import CONF_PORT, DEFAULT_PORT
from .udp import UdpHandler

import binascii

_LOGGER = logging.getLogger(__name__)

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST, default="192.168.4.120"): cv.string,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): cv.positive_int,
    }
)


def rgb(red: int, green: int, blue: int) -> str:
    rgb_packet = []
    rgb_packet.append(red)
    rgb_packet.append(green)
    rgb_packet.append(blue)
    rgb_packet.append(0)

    res = binascii.hexlify(bytearray(rgb_packet))
    return binascii.unhexlify(res)


UDP_IP = "192.168.4.120"
UDP_PORT = DEFAULT_PORT

SCAN_INTERVAL = timedelta(minutes=10)


class Ws281XLedStrip:
    class StripIndex(IntEnum):
        """Pattern (light effect) bitflags."""

        ALL = 0
        LOWER = 1
        UPPER = 2

    def __init__(
        self,
        udp_ip: str,
        udp_port: int,
        strip_index: StripIndex = StripIndex.ALL,
    ) -> None:
        self._ip = udp_ip
        self._udp_handler = UdpHandler(udp_ip, udp_port)
        self._strip_index = strip_index
        self._unique_id = f"ledstrip-{udp_ip}:{udp_port}-{self._strip_index}"
        self._color = self.rgb_byte_array(127, 127, 127)
        self._is_on = True

    def turn_on(self):
        self._is_on = True
        self._send(self._color)

    def turn_off(self):
        self._color = self.rgb_byte_array(0, 0, 0)
        self._is_on = False
        self._send(self._color)

    def is_strip_on(self) -> bool:
        return self._is_on

    def ip(self):
        return self._ip

    def set_rgb(self, red: int, green: int, blue: int) -> None:
        self._color = self.rgb_byte_array(red, green, blue)
        print(self._color)
        self._send(self._color)

    def _send(self, color: str) -> None:
        self._udp_handler.send(color)

    def get_rgb(self):
        return self._color

    def unique_id(self) -> str:
        return self._unique_id

    def rgb_byte_array(self, red: int, green: int, blue: int) -> str:
        rgb_packet = []
        rgb_packet.append(red)
        rgb_packet.append(green)
        rgb_packet.append(blue)
        rgb_packet.append(self._strip_index)

        res = binascii.hexlify(bytearray(rgb_packet))

        return binascii.unhexlify(res)

    @property
    def name(self) -> str:
        return f"chipha-led-strip[{self._strip_index}]"


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
):
    # add all chipha light entities
    lower = LightStrip(
        Ws281XLedStrip(UDP_IP, UDP_PORT, strip_index=Ws281XLedStrip.StripIndex.LOWER)
    )
    upper = LightStrip(
        Ws281XLedStrip(UDP_IP, UDP_PORT, strip_index=Ws281XLedStrip.StripIndex.UPPER)
    )

    async_add_entities([lower, upper])


ATTR_IP = "IP"


# https://developers.home-assistant.io/docs/integration_fetching_data
SCAN_INTERVAL = timedelta(seconds=30)


class LightStrip(LightEntity):
    """Representation of WS2812B UDP LED STRIP."""

    DEFAULT_ON_COLOR = (0, 255, 0)

    def __init__(self, light) -> None:
        self._light = light
        self._name = light.name
        self._state = None
        self._unique_id = light.unique_id()
        self.color_mode = ColorMode.RGB
        self._rgb_color = None
        self._icon = "mdi:lightbulb"
        self.attrs: Dict[str, Any] = {ATTR_IP, self._light.ip()}

    @property
    def name(self) -> str:
        """Return the display name of this light."""
        return self._name

    @property
    def state(self):
        return self._state

    """
    @property
    def state(self) -> Optional[str]:
        return self._state
    """

    def get_color_mode(self):
        return ColorMode.RGB

    # @property
    # def is_on(self) -> bool | None:
    #    """Return true if light is on."""
    #    return self._state

    def turn_on(self, **kwargs: Any) -> None:
        """Instruct the light to turn on."""
        self._state = STATE_ON
        _rgb = kwargs.get(ATTR_RGB_COLOR)
        self._rgb_color = _rgb

        if self._rgb_color is None:
            self._rgb_color = self.DEFAULT_ON_COLOR

        self._light.set_rgb(self._rgb_color[0], self._rgb_color[1], self._rgb_color[2])
        self._light.turn_on()

    def turn_off(self, **kwargs: Any) -> None:
        self._state = STATE_OFF
        """Instruct the light to turn off."""
        self._rgb_color = (0, 0, 0)
        self._light.turn_off()

    """
    @property
    def supported_features(self):
        # Return the flag supported features
        return SUPPORTED_LIGHT_FEATURES
    """

    @property
    def supported_color_modes(self):
        return [ColorMode.RGB]

    @property
    def rgb_color(self):
        return self._rgb_color

    @property
    def icon(self):
        if self._icon:
            return "mdi:lightbulb-on"

        return "mdi:lightbulb-off"

    @property
    def device_state_attributes(self) -> Dict[str, Any]:
        return self.attrs

    @property
    def is_on(self) -> bool | None:
        """Return true if light is on."""
        return self._state

    def set_rgb_color(self, rgb: tuple):
        self._rgb_color = rgb
        self._light.set_rgb(self._rgb_color[0], self._rgb_color[1], self._rgb_color[2])

    def get_rgb_color(self):
        return self._rgb_color

    @property
    def unique_id(self):
        return self._unique_id

    async def async_update(self) -> None:
        """Fetch new state data for this light.

        This is the only method that should fetch new data for Home Assistant.
        """
        try:
            # self._rgb_color = self._light.get_rgb()
            self._state = STATE_ON if self._light.is_strip_on() else STATE_OFF
            print(f"Update {self._rgb_color}:{self._state}")
        except:
            _LOGGER.error("Unable to retrieve state from light")
        # self._light.update()
        # self._state = self._light.is_on()
        # self._brightness = self._light.brightness
