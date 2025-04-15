from datetime import timedelta
from homeassistant.helpers.event import async_track_time_interval
import logging
import async_timeout
from .api import fetch_prices

from .consts import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass, config):
    async def fetch_prices(_now):
        try:
            with async_timeout.timeout(10):
                data = await fetch_prices()
                # Process and update states
                hass.states.async_set(
                    f"{DOMAIN}.prices",
                    data["prices"][0],
                    {"hourly_prices": data["prices"]},
                )
                cheapest = min(data["prices"], key=lambda x: x["price"]["total"])
                hass.states.async_set(f"{DOMAIN}.cheapest_hour", cheapest["date"])
        except Exception as e:
            _LOGGER.error(f"Failed to fetch electricity prices: {e}")

    async_track_time_interval(hass, fetch_prices, timedelta(hours=12))
    return True
