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

from statistics import mean
from typing import List, Dict, Optional
from datetime import datetime, timedelta, time
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.event import (
    async_track_point_in_time,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.config_entries import ConfigEntry
import async_timeout
import logging
from .api import fetch_prices
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(
    hass: HomeAssistant, config: ConfigType, async_add_entities, discovery_info=None
):
    pass


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
):
    data = hass.data[DOMAIN][entry.entry_id]
    sensor = ElectricityPriceSensor(data["product"], data["zone"])
    cheapest_sensor = CheapestHourSensor(sensor)
    cheapest_sensor_2h = CheapestHourSpan2hSensor(sensor)
    cheapest_sensor_3h = CheapestHourSpan3hSensor(sensor)

    async_add_entities(
        [sensor, cheapest_sensor, cheapest_sensor_2h, cheapest_sensor_3h]
    )

    def schedule_fetch(at_time: time):
        now = datetime.now()
        next_run = datetime.combine(now.date(), at_time)
        if next_run < now:
            next_run += timedelta(days=1)
        async_track_point_in_time(hass, fetch_data_at, next_run)

    async def update_data(_now):
        await sensor.async_update_data()
        cheapest_sensor.async_update_state()
        cheapest_sensor_2h.async_update_state()
        cheapest_sensor_3h.async_update_state()

    async def fetch_data_at(time):
        await update_data(time)
        # Re-schedule for next day
        next_run = time + timedelta(days=1)
        async_track_point_in_time(hass, fetch_data_at, next_run)

    # Schedule fetches at 00:00 and 13:30
    schedule_fetch(time(0, 0))
    schedule_fetch(time(13, 30))

    # Fetch now
    await update_data(datetime.now())

    _LOGGER.info("Entities have been added")


class ElectricityPriceSensor(SensorEntity):
    def __init__(self, product_id: str, zone: str):
        self._attr_name = "Electricity Prices"
        self._attr_unique_id = "{DOMAIN}_prices"
        self._state = None
        self._attr_extra_state_attributes = {
            "description": "Fetches hourly electricity prices for use in HomeAssistant.",
            "attribution": "Electricity pricing data provided by Strømligning. https://stromligning.dk. N1 distribution prices scraped from https://n1.dk/gaeldende-priser.",
            "unit": "DKK/kWh",
        }
        self._product_id = product_id
        self._zone = zone

    async def async_update_data(self):
        try:
            with async_timeout.timeout(10):
                data = await fetch_prices(
                    price_area=self._zone, product=self._product_id
                )
                self._attr_extra_state_attributes["hourly_prices"] = list(
                    map(
                        lambda p: {"date": p["date"], "price": p["price"]["total"]},
                        data["prices"],
                    )
                )
                self._state = data["prices"][0]["price"]["total"] if data else None
        except Exception as e:
            _LOGGER.error(f"Failed to fetch electricity prices: {e}")
            self._state = None

    @property
    def native_value(self):
        return self._state

    def async_update_state(self):
        self.async_schedule_update_ha_state()


class CheapestHourSensor(SensorEntity):
    def __init__(self, price_sensor: ElectricityPriceSensor):
        self._attr_name = "Cheapest Hour"
        self._attr_unique_id = "{DOMAIN}_cheapest_hour"
        self._state = None
        self._price_sensor = price_sensor
        self._attr_extra_state_attributes = {}

    def async_update_state(self):
        data = self._price_sensor.extra_state_attributes.get("hourly_prices")
        if data:
            cheapest = min(data, key=lambda x: x["price"])
            self._state = cheapest["date"]
            self._attr_extra_state_attributes = cheapest
        else:
            self._state = None
        self.async_schedule_update_ha_state()

    @property
    def native_value(self):
        return self._state


class CheapestHourSpan2hSensor(SensorEntity):
    def __init__(self, price_sensor: ElectricityPriceSensor):
        self._attr_name = "Cheapest Hour Span (2 hours)"
        self._attr_unique_id = "{DOMAIN}_cheapest_hour_span_2h"
        self._state = None
        self._price_sensor = price_sensor
        self._attr_extra_state_attributes = {}

    def async_update_state(self):
        data = self._price_sensor.extra_state_attributes.get("hourly_prices")
        if data:
            cheapest_span = _find_cheapest_hour_span(data, 2)
            self._state = cheapest_span["avg_price"]
            self._attr_extra_state_attributes = cheapest_span
        else:
            self._state = None
        self.async_schedule_update_ha_state()

    @property
    def native_value(self):
        return self._state


class CheapestHourSpan3hSensor(SensorEntity):
    def __init__(self, price_sensor: ElectricityPriceSensor):
        self._attr_name = "Cheapest Hour Span (3 hours)"
        self._attr_unique_id = "{DOMAIN}_cheapest_hour_span_3h"
        self._state = None
        self._price_sensor = price_sensor
        self._attr_extra_state_attributes = {}

    def async_update_state(self):
        data = self._price_sensor.extra_state_attributes.get("hourly_prices")
        if data:
            cheapest_span = _find_cheapest_hour_span(data, 3)
            self._state = cheapest_span["avg_price"]
            self._attr_extra_state_attributes = cheapest_span
        else:
            self._state = None
        self.async_schedule_update_ha_state()

    @property
    def native_value(self):
        return self._state


def _find_cheapest_hour_span(data: List[Dict], span_hours: int) -> Optional[Dict]:
    """
    Finds the cheapest consecutive hour span.

    Args:
        data: List of dicts with 'datetime' and 'price' keys
        span_hours: Number of consecutive hours in the span

    Returns:
        A dict with 'start', 'end', 'total_price', 'avg_price', and 'entries' of the span
    """
    if len(data) < span_hours:
        return None

    cheapest_span = None
    min_total = float("inf")

    for i in range(len(data) - span_hours + 1):
        window = data[i : i + span_hours]
        prices = list(entry["price"] for entry in window)
        total = sum(prices)
        avg_price = mean(prices)

        if total < min_total:
            min_total = total
            cheapest_span = {
                "start": window[0]["date"],
                "end": window[-1]["date"],
                "avg_price": avg_price,
                "total_price": total,
                "entries": window,
            }

    return cheapest_span
