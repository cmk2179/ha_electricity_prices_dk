# Show cheapest price for a given hour span

Add a markdown content card to the dashboard.

Copy/paste the code below to set up the card.

**2 hour span**

```
{% set total = states('sensor.cheapest_hour_span_2_hours') %}
{% if total not in ['unknown', 'unavailable'] %}
  **Start**: {{ as_local(as_datetime(state_attr('sensor.cheapest_hour_span_2_hours', 'start'))).strftime('%Y-%m-%d %H:%M') }}
  **End**: {{ as_local(as_datetime(state_attr('sensor.cheapest_hour_span_2_hours', 'end'))).strftime('%Y-%m-%d %H:%M') }}
  **Avg. price**: {{ state_attr('sensor.cheapest_hour_span_2_hours', 'avg_price') | round(2) }} DKK/KWh
{% else %}
  unknown
{% endif %}
```

**3 hour span**

```
{% set total = states('sensor.cheapest_hour_span_3_hours') %}
{% if total not in ['unknown', 'unavailable'] %}
  **Start**: {{ as_local(as_datetime(state_attr('sensor.cheapest_hour_span_3_hours', 'start'))).strftime('%Y-%m-%d %H:%M') }}
  **End**: {{ as_local(as_datetime(state_attr('sensor.cheapest_hour_span_3_hours', 'end'))).strftime('%Y-%m-%d %H:%M') }}
  **Avg. price**: {{ state_attr('sensor.cheapest_hour_span_3_hours', 'avg_price') | round(2) }} DKK/KWh
{% else %}
  unknown
{% endif %}
```
