from homeassistant import config_entries
from .const import DOMAIN
import voluptuous as vol
from collections import OrderedDict
import logging
from typing import Any
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
import re
from homeassistant.data_entry_flow import section


_LOGGER = logging.getLogger(__name__)


class LSLightsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    MINOR_VERSION = 1

    def __init__(self):
        self._input: dict[str, Any] = {}

    def validate_ipv4(self, ip: str):
        pattern = re.compile(
            r"^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
        )
        return bool(pattern.match(ip))

    def validate_ipv6(self, ip: str):
        pattern = re.compile(
            r"^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$|^([0-9a-fA-F]{1,4}:){1,7}:$|^::([0-9a-fA-F]{1,4}:){0,7}[0-9a-fA-F]{1,4}$"
        )
        return bool(pattern.match(ip))

    def validate_ip(self, ip: str):
        if self.validate_ipv4(ip):
            return True
        elif self.validate_ipv6(ip):
            return True
        else:
            return False

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

        _LOGGER.info("Create entry")

        ip_address = user_input.get("ip_config", {}).get("ip_address", "127.0.0.1")

        if not self.validate_ip(ip_address):
            errors["ip_address"] = "Invalid IP Address"
            return self.async_show_form(
                step_id="user", data_schema=vol.Schema(data_schema), errors=errors
            )

        return self.async_create_entry(title="CHIPPA", data={"ip_address": ip_address})
