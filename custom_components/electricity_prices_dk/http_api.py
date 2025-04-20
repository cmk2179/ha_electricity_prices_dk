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

from datetime import datetime
import aiohttp


if __package__ is None or __package__ == "":
    from n1_utils import get_tarif_for_hour, get_n1_tarifs
    from const import LOCAL_TZ
else:
    from .n1_utils import get_tarif_for_hour, get_n1_tarifs
    from .const import LOCAL_TZ

API_BASE = "https://stromligning.dk/api"


def filter_and_map_prices(area: int, includesVat: bool, data: any) -> any:
    data = {}
    for item in data:
        if item["area"] == area and item["includesVat"] == includesVat:
            for date_str, price_time in item["data"]:
                time = price_time["x"]
                price = price_time["y"]

                dt_str = f"{date_str}T{time}:00"
                date = datetime.strptime(dt_str, "%Y-%m-%dT%H:%M")

                data[date.isoformat()] = price
    return data


async def get_spot_prices(
    price_area: str, product: str, from_date: str, to_date: str
) -> any:
    data = {}

    n1_tarifs = await get_n1_tarifs()

    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{API_BASE}/prices?productId={product}&priceArea={price_area}&from={from_date}&to={to_date}",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
        ) as res:
            if res.status != 200:
                raise Exception(
                    f"Could not get spot prices from API. [status={res.status}, body={await res.text()}]"
                )
            data = await res.json()

            prices_per_hour = {}
            for price in data["prices"]:
                date = datetime.fromisoformat(price["date"]).astimezone(LOCAL_TZ)
                n1_tarif_hour = get_tarif_for_hour(date, n1_tarifs)
                n1_tarif_hour_vat = 0.25 * n1_tarif_hour
                n1_tarif_hour_total = n1_tarif_hour + n1_tarif_hour_vat
                price["details"]["distribution"] = {
                    "value": n1_tarif_hour,
                    "vat": n1_tarif_hour_vat,
                    "total": n1_tarif_hour_total,
                }
                price["price"]["value"] += n1_tarif_hour
                price["price"]["vat"] += n1_tarif_hour_vat
                price["price"]["total"] += n1_tarif_hour_total

                prices_per_hour[price["date"]] = price
    return data


async def get_companies():
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{API_BASE}/companies?region=DK1",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
        ) as res:
            if res.status != 200:
                raise Exception(
                    f"Could not get spot prices from API. [status={res.status}, body={await res.text()}]"
                )

            return await res.json()


async def get_zones():
    # Hardcoded for now - shouldn't change.. But just in case, it's been prepared for async
    return ["DK1", "DK2"]
