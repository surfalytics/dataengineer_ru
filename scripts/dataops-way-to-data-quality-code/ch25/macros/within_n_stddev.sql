{% test within_n_stddev(model, column_name, date_column, lookback_days, n_stddev) %}
with history as (
    select avg({{ column_name }}) as mean, stddev({{ column_name }}) as deviation
    from {{ model }}
    where {{ date_column }} >= current_date - interval '{{ lookback_days }} days'
      and {{ date_column }} < current_date
), today as (
    select avg({{ column_name }}) as mean
    from {{ model }}
    where {{ date_column }} = current_date
)
select today.mean
from today cross join history
where history.deviation > 0
  and abs(today.mean - history.mean) > {{ n_stddev }} * history.deviation
{% endtest %}
