# Show cheapest price during the next 24 hours

Add a markdown content card to the dashboard.

Copy/paste the code below to set up the card.

```
{% set ts = states('sensor.cheapest_hour') %} {% if ts not in ['unknown', 'unavailable'] %}
  {{ as_local(as_datetime(ts)).strftime('%Y-%m-%d %H:%M') }} @ {{ state_attr('sensor.cheapest_hour', 'price') | round(2) }} DKK/KWh
{% else %}
  unknown
{% endif %}
```
