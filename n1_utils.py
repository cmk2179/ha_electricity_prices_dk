from datetime import datetime
import json
import requests
from bs4 import BeautifulSoup


def parse_number(num: str) -> int:
    return float(num.replace(",", "."))


def get_n1_tarifs():
    res = requests.get("https://n1.dk/gaeldende-priser")
    soup = BeautifulSoup(res.text, features="html.parser")

    for tag in soup(["script", "style"]):
        tag.decompose()

    data = {}
    # Lavlast sommer, 00:00-06:00, april til september
    data["low_load_summer"] = (
        parse_number(
            soup.select_one(".price-table tr:nth-child(2) td:nth-child(2)").get_text(
                strip=True
            )
        )
        / 100
    )

    # Højlast sommer, 06:00-17:00 og 21:00-24:00, april til september
    data["high_load_summer"] = (
        parse_number(
            soup.select_one(".price-table tr:nth-child(3) td:nth-child(2)").get_text(
                strip=True
            )
        )
        / 100
    )

    # Spidslast sommer, 17:00-21:00, april til september
    data["peak_load_summer"] = (
        parse_number(
            soup.select_one(".price-table tr:nth-child(4) td:nth-child(2)").get_text(
                strip=True
            )
        )
        / 100
    )

    # Lavlast vinter, 00:00-06:00, oktober til marts
    data["low_load_winter"] = (
        parse_number(
            soup.select_one(".price-table tr:nth-child(5) td:nth-child(2)").get_text(
                strip=True
            )
        )
        / 100
    )

    # Højlast vinter, 06:00-17:00 og 21:00-24:00, oktober til marts
    data["high_load_winter"] = (
        parse_number(
            soup.select_one(".price-table tr:nth-child(6) td:nth-child(2)").get_text(
                strip=True
            )
        )
        / 100
    )

    # Spidslast vinter, 17:00-21:00, oktober til marts
    data["peak_load_winter"] = (
        parse_number(
            soup.select_one(".price-table tr:nth-child(7) td:nth-child(2)").get_text(
                strip=True
            )
        )
        / 100
    )

    return data


def get_tarif_for_hour(date: datetime, tarifs: dict) -> float:
    if 4 <= date.month <= 9:
        # summer
        if 0 <= date.hour < 6:
            # low load
            return tarifs["low_load_summer"]
        if 6 <= date.hour < 17 or 21 <= date.hour <= 23:
            # high load
            return tarifs["high_load_summer"]
        if 17 <= date.hour < 21:
            # low load
            return tarifs["peak_load_summer"]

    if date.month >= 1 or date.month >= 10:
        # winter
        if 0 <= date.hour < 6:
            # low load
            return tarifs["low_load_winter"]
        if 6 <= date.hour < 17 or 21 <= date.hour <= 23:
            # high load
            return tarifs["high_load_winter"]
        if 17 <= date.hour < 21:
            # low load
            return tarifs["peak_load_winter"]


if __name__ == "__main__":
    n1_prices = get_n1_tarifs()
    print(json.dumps(n1_prices, indent=2))
