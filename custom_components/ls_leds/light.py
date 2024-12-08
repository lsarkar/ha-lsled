"""Platform for light integration."""

from __future__ import annotations

from datetime import timedelta
from enum import IntEnum
import logging
from typing import Any

from homeassistant.components.light import ATTR_RGB_COLOR, ColorMode, LightEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_OFF, STATE_ON
from homeassistant.core import HomeAssistant

from .udp import UdpHandler
from .datapacket import DataPacket

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, config: ConfigEntry, async_add_entities
):
    # add all chipha light entities
    udp_ip_address = config.data["ip_address"]
    udp_ip_port = config.data["ip_port"]
    _LOGGER.info(udp_ip_address)
    _LOGGER.info(udp_ip_port)

    lower = LightStrip(
        Ws281XLedStrip(
            udp_ip_address, udp_ip_port, strip_index=Ws281XLedStrip.StripIndex.LOWER
        )
    )
    upper = LightStrip(
        Ws281XLedStrip(
            udp_ip_address, udp_ip_port, strip_index=Ws281XLedStrip.StripIndex.UPPER
        )
    )

    async_add_entities([lower, upper])


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
        self._is_on = False

    async def async_turn_on(self):
        self._is_on = True
        await self._send_async(self._color)

    async def async_turn_off(self):
        self._is_on = False
        self._color = self.rgb_byte_array(0, 0, 0)
        await self._send_async(self._color)

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

    async def _send_async(self, color: str) -> None:
        await self._udp_handler.send_async(color)

    def get_rgb(self):
        return self._color

    def unique_id(self) -> str:
        return self._unique_id

    def rgb_byte_array(self, red: int, green: int, blue: int) -> str:
        """Construct an rgb byte array."""
        return DataPacket.construct_rgb(red, green, blue, self._strip_index)

    @property
    def name(self) -> str:
        return f"chipha-led-strip-{self._strip_index}"


# https://developers.home-assistant.io/docs/integration_fetching_data
SCAN_INTERVAL = timedelta(seconds=30)


class LightStrip(LightEntity):
    """Representation of CHIPHA LED STRIP."""

    DEFAULT_ON_COLOR = (0, 255, 0)

    def __init__(self, light) -> None:
        self._light = light
        self._name = light.name
        self._state = STATE_OFF
        self._brightness = 0
        self._unique_id = light.unique_id()
        self.color_mode = ColorMode.RGB
        self._rgb_color = None
        self._icon = "mdi:lightbulb"
        self.attrs: dict[str, Any] = {"IP": self._light.ip(), "ID": self._unique_id}

    @property
    def name(self) -> str:
        """Return the display name of this light."""
        return self._name

    @property
    def state(self):
        "Return the state of the light."
        return self._state

    @property
    def supported_color_modes(self):
        """Return the supported colors of this light."""
        return ColorMode.RGB

    @property
    def brightness(self):
        """Return the brightness of this light."""
        return self._brightness

    def get_color_mode(self):
        """Return the supported color mode."""
        return ColorMode.RGB

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Instruct the light to turn on."""
        self._state = STATE_ON
        self._rgb_color = kwargs.get(ATTR_RGB_COLOR)
        self._brightness = kwargs.get("brightness", 255)

        if self._rgb_color is None:
            self._rgb_color = self.DEFAULT_ON_COLOR

        _LOGGER.info("Turn on light")

        self._light.set_rgb(self._rgb_color[0], self._rgb_color[1], self._rgb_color[2])
        await self._light.async_turn_on()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        self._state = STATE_OFF
        self._brightness = 0
        self._rgb_color = (0, 0, 0)
        await self._light.async_turn_off()

    @property
    def supported_color_modes(self):
        """Return supported color modes."""
        return [ColorMode.RGB]

    @property
    def rgb_color(self):
        """Return the rgb color of the light."""
        return self._rgb_color

    @property
    def icon(self):
        """Return the icon of the light based on the state."""
        if self._state == STATE_ON:
            return "mdi:lightbulb-on"

        return "mdi:lightbulb-off"

    @property
    def extra_state_attributes(self):
        """Return the custom attributes of the light."""
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
        """Return a unique id for this light."""
        return self._unique_id

    async def async_update(self) -> None:
        """Fetch new state data for this light.

        This is the only method that should fetch new data for Home Assistant.
        """
        try:
            # self._rgb_color = self._light.get_rgb()
            self._state = STATE_ON if self._light.is_strip_on() else STATE_OFF
            _LOGGER.info(f"Update {self._rgb_color}:{self._state}")
        except:
            _LOGGER.error("Unable to retrieve state from light")
        # self._light.update()
        # self._state = self._light.is_on()
        # self._brightness = self._light.brightness
