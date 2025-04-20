# An integration for Home Assistant that fetches electricity prices and makes the data available via sensors.
# Copyright (C) 2025  Chris Opstrup

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import voluptuous as vol
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.core import callback
import logging
from awesomeversion import AwesomeVersion
from homeassistant.const import __version__ as HAVERSION
from homeassistant.config_entries import ConfigEntry, OptionsFlow, ConfigFlow
from custom_components.electricity_prices_dk.http_api import get_companies, get_zones

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class ElectricityPricesConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1
    MINOR_VERSION = 1

    def __init__(self):
        self._user_input = {}

    async def async_step_user(self, user_input=None):
        """Step 1: select company"""
        if user_input is not None:
            self._user_input.update(user_input)
            return await self.async_step_product()

        self._companies = await get_companies()
        companies = {}
        for company in self._companies:
            companies[company["_id"]] = company["name"]

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required("company"): vol.In(companies)}),
        )

    async def async_step_product(self, user_input=None):
        """Step 2: select product based on company"""
        if user_input is not None:
            self._user_input.update(user_input)
            return await self.async_step_zone()

        products = self._get_products()
        if not products:
            return self.async_abort(reason="cannot_connect")

        return self.async_show_form(
            step_id="product",
            data_schema=vol.Schema({vol.Required("product"): vol.In(products)}),
        )

    def _get_products(self):
        user_company_id = self._user_input["company"]
        company = next(
            filter(lambda c: c["_id"] == user_company_id, self._companies), None
        )

        if company is not None:
            products = {}
            for product in company["products"]:
                products[product["id"]] = product["name"]
            return products

        return None

    async def async_step_zone(self, user_input=None):
        """Step 3: select zone based on product"""
        if user_input is not None:
            self._user_input.update(user_input)
            return self.async_create_entry(
                title="Electricity Prices", data=self._user_input
            )

        zones = await get_zones()
        if not zones:
            return self.async_abort(reason="cannot_connect")

        return self.async_show_form(
            step_id="zone",
            data_schema=vol.Schema({vol.Required("zone"): vol.In(zones)}),
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry):
        return ElectricityPricesOptionsFlowHandler(config_entry)


class ElectricityPricesOptionsFlowHandler(OptionsFlow):
    VERSION = 1
    MINOR_VERSION = 0

    def __init__(self, config_entry: ConfigEntry):
        # To ensure backwards compatibility, we should set the config_entry manually for older versions.
        # For newer versions it's available as a read only property.
        # See https://github.com/home-assistant/core/pull/129562
        if AwesomeVersion(HAVERSION) < "2024.11.99":
            self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Pre-fill form with existing values
        config = self.config_entry.options or self.config_entry.data
        company_id = config.get("company", "")
        product_id = config.get("product", "")
        zone = config.get("zone", "")

        self._companies = await get_companies()
        companies = {}
        for company in self._companies:
            companies[company["_id"]] = company["name"]

        self._products = self._get_products(company_id)
        products = {}
        for product in self._products:
            products[product["id"]] = product["name"]

        zones = await get_zones()

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required("company", default=company_id): vol.In(companies),
                    vol.Required("product", default=product_id): vol.In(products),
                    vol.Required("zone", default=zone): vol.In(zones),
                }
            ),
        )

    def _get_products(self, company_id: int):
        for company in self._companies:
            if company["_id"] == company_id:
                return company["products"]
        return []
