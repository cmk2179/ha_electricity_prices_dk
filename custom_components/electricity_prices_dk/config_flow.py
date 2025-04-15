import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import logging
from custom_components.electricity_prices_dk.http_api import get_companies, get_zones

from .consts import DOMAIN

_LOGGER = logging.getLogger(__name__)


class ElectricityPricesConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    MINOR_VERSION = 0

    def __init__(self):
        self._user_input = {}
        self._companies = get_companies()

    async def async_step_user(self, user_input=None):
        """Step 1: select company"""
        if user_input is not None:
            self._user_input.update(user_input)
            return await self.async_step_product()

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

    def get_products(self):
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

        zones = get_zones()
        if not zones:
            return self.async_abort(reason="cannot_connect")

        return self.async_show_form(
            step_id="zone",
            data_schema=vol.Schema({vol.Required("zone"): vol.In(zones)}),
        )
