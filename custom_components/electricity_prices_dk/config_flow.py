import voluptuous as vol
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import logging
from homeassistant.config_entries import ConfigEntry, OptionsFlow, ConfigFlow
from custom_components.electricity_prices_dk.http_api import get_companies, get_zones

from .consts import DOMAIN

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


class ElectricityPricesOptionsFlowHandler(OptionsFlow):
    VERSION = 1
    MINOR_VERSION = 0

    def __init__(self, config_entry: ConfigEntry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Pre-fill form with existing values
        current = self.config_entry.options or self.config_entry.data

        self._companies = await get_companies()
        companies = {}
        for company in self._companies:
            companies[company["_id"]] = company["name"]

        company_id = current.get("company", "")

        self._products = self._get_products(company_id)
        products = {}
        for product in self._products:
            products[product["_id"]] = product["name"]
        product_id = current.get("product", "")

        zone = current.get("zone", "")
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


async def async_get_options_flow(config_entry: ConfigEntry):
    return ElectricityPricesOptionsFlowHandler(config_entry)
