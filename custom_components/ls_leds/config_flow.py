from homeassistant import config_entries
from .const import DOMAIN
import voluptuous as vol
from collections import OrderedDict
import logging
from typing import Any
from homeassistant.data_entry_flow import section
from .udp import UdpHandler

_LOGGER = logging.getLogger(__name__)


class LSLightsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    MINOR_VERSION = 1

    def __init__(self):
        self._input: dict[str, Any] = {}

    async def async_step_user(self, user_input: dict[str, Any]):
        data_schema = {
            "ip_config": section(
                vol.Schema({vol.Required("ip_address", default="127.0.0.1"): str}),
                {"collapsed": False},
            )
        }

        errors = {}
        _LOGGER.info("Show user form")

        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=vol.Schema(data_schema), errors=errors
            )

        ip_address = user_input.get("ip_config", {}).get("ip_address", "127.0.0.1")

        _LOGGER.info("Perform IP address validation")
        if not UdpHandler.validate_ip(ip_address):
            errors["ip_address"] = "Invalid IP Address"
            return self.async_show_form(
                step_id="user", data_schema=vol.Schema(data_schema), errors=errors
            )

        _LOGGER.info("Create entry")

        return self.async_create_entry(title="CHIPPA", data={"ip_address": ip_address})
