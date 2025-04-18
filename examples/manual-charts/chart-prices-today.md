# Manual chart showing prices for today

When adding a card to the dashboard, scroll to the bottom and select manual card.

Copy/paste the yaml config below to set up the graph.

```yaml
type: custom:apexcharts-card
header:
  title: Electricity Prices (Today)
  show: true
graph_span: 24h
span:
  start: day
series:
  - entity: sensor.electricity_prices
    type: column
    float_precision: 2
    name: Price
    data_generator: |
      return entity.attributes.hourly_prices.map(item => {
        return [new Date(item.date), item.price];
      });
    unit: DKK/kWh
```

## Prequisites

- [apexcharts-card](https://github.com/RomRider/apexcharts-card)
