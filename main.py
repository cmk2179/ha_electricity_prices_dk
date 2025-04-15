import sys
import json
from custom_components.electricity_prices_dk.api import fetch_prices
import asyncio


async def main():
    prices = await fetch_prices(price_area="DK1", product="groen_ok_el_spot")
    print(json.dumps(prices, indent=2))


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
