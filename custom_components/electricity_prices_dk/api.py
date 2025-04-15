import sys
from datetime import datetime, timedelta, time, timezone
from zoneinfo import ZoneInfo
from .http_api import get_spot_prices


async def fetch_prices(price_area: str, product: str):
    now = datetime.now(ZoneInfo("Europe/Copenhagen"))
    start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = now.replace(hour=23, minute=0, second=0, microsecond=0)

    if now.hour > 13:
        # prices for tomorrow are available after 13, so lets get them as well
        end_date = end_date + timedelta(days=1)

    start_date_str = (
        start_date.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    )
    end_date_str = end_date.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

    print(f"From: {start_date_str}")
    print(f"To: {end_date_str}")

    return get_spot_prices(
        price_area=price_area,
        product=product,
        from_date=start_date_str,
        to_date=end_date_str,
    )


# TODO: Fetch a list of companies from the API - this list includes products
def fetch_companies():
    pass


# Hardcoded for now - shouldn't change..
def fetch_zones():
    return ["DK1", "DK2"]


if __name__ == "__main__":
    try:
        import json

        data = fetch_prices(price_area="DK1", product="groen_ok_el_spot")
        print(json.dumps(data, indent=2))
    except Exception as e:
        print(e, file=sys.stderr)
