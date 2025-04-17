import sys
from datetime import datetime, timedelta, time, timezone
from zoneinfo import ZoneInfo

if __package__ is None or __package__ == "":
    from http_api import get_spot_prices
    from consts import LOCAL_TZ
else:
    from .http_api import get_spot_prices
    from .consts import LOCAL_TZ


async def fetch_prices(price_area: str, product: str):
    now = datetime.now(LOCAL_TZ)
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

    return await get_spot_prices(
        price_area=price_area,
        product=product,
        from_date=start_date_str,
        to_date=end_date_str,
    )


if __name__ == "__main__":
    try:
        import sys
        import asyncio

        async def main():
            import json

            data = await fetch_prices(price_area="DK1", product="groen_ok_el_spot")
            print(json.dumps(data, indent=2))

        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        asyncio.run(main())
    except Exception as e:
        print(e, file=sys.stderr)
