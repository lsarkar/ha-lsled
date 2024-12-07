import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow

from .const import DEFAULT_IP, DEFAULT_PORT, DOMAIN
from .udp import UdpHandler

_LOGGER = logging.getLogger(__name__)


class LSLightsConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1
    MINOR_VERSION = 1

    def __init__(self):
        self._input: dict[str, Any] = {}

    async def async_step_user(self, user_input: dict[str, Any]):
        data_schema = {
            vol.Required("ip_address", default=DEFAULT_IP): str,
            vol.Required("ip_port", default=DEFAULT_PORT): vol.All(
                int, vol.Range(min=1024, max=65535)
            ),
        }

        errors = {}
        _LOGGER.info("Show user form")

        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=vol.Schema(data_schema), errors=errors
            )

        ip_address = user_input.get("ip_address")
        ip_port = user_input.get("ip_port")

        _LOGGER.info("Perform IP address validation")
        if not UdpHandler.validate_ip(ip_address):
            _LOGGER.warning("Failed IP validation")
            errors["ip_address"] = "Invalid IP address"
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(data_schema),
                errors=errors,
            )

        data = {"ip_address": ip_address, "ip_port": ip_port}
        _LOGGER.info("Create entry with data", extra=(data))

        return self.async_create_entry(title="CHIPPA", data=data)
