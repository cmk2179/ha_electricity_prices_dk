from datetime import datetime
import requests
from functools import reduce
from n1_utils import get_tarif_for_hour, get_n1_tarifs

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


def get_spot_prices(price_area: str, product: str, from_date: str, to_date: str) -> any:
    data = {}

    # TODO: Get spot prices from strømligning - it seems they are the most accurate ones: https://stromligning.dk/api/docs/#/Prices/get_api_prices
    res = requests.get(
        f"{API_BASE}/prices?productId={product}&priceArea={price_area}&from={from_date}&to={to_date}",
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
    )

    if res.status_code != 200:
        raise Exception(
            f"Could not get spot prices from API. [status={res.status_code}, body={res.text}]"
        )
    data = res.json()

    # TODO: Get N1 prices from https://n1.dk/gaeldende-priser
    n1_tarifs = get_n1_tarifs()

    # TODO: Add N1 prices to distribution costs (system tarif + nettarif + N1 tarif)
    prices_per_hour = {}
    for price in data["prices"]:
        n1_tarif_hour = get_tarif_for_hour(
            datetime.fromisoformat(price["date"]), n1_tarifs
        )
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


def get_companies():
    res = requests.get(
        f"{API_BASE}/companies?region=DK1",
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
    )

    if res.status_code != 200:
        raise Exception(
            f"Could not get spot prices from API. [status={res.status_code}, body={res.text}]"
        )

    return res.json()
