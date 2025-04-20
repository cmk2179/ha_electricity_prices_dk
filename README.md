# Electricity prices

A Homeassistant integration that makes electricity prices available in Homeassistant for triggering automations and/or making graphs.

# Attribution

Most prices are retrieved from Strømligning - please refer to their usage guide and documentation: https://stromligning.dk/api/docs/

Distribution prices are fetched from N1s website: https://n1.dk/gaeldende-priser

# Install in Home Assistant

## Using HACS (Home Assistant Community Store)

First see the documentation on downloading and configuring HACS: https://www.hacs.xyz/docs/use/

1. Add a custom repository to HACS: https://www.hacs.xyz/docs/faq/custom_repositories/
2. Add this github repo: https://github.com/cmk2179/ha_electricity_prices_dk
3. Choose type: Integration
4. Search for the integration in HACS (Electricity prices)
5. Download the integration via HACS
6. Restart Home Assistant
7. Now you can setup the integration in **Settings** -> **Devices & services** -> **Add integration**

## Manual

1. Download the release you want
2. Unzip and upload the files to /config/custom_components
3. Restart Home Assistant
4. Now you can setup the integration in **Settings** -> **Devices & services** -> **Add integration**

# Future work

- Support other electricity companies.
