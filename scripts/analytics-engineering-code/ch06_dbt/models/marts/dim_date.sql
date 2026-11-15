-- Аналог dbt_date.get_date_dimension("2022-01-01", "2024-12-31").
-- Макрос из dbt_date использует to_char, а в DuckDB этой функции нет.
select
    cast(d as date) as date_day,
    year(d)         as year_number,
    quarter(d)      as quarter_of_year,
    month(d)        as month_of_year
from generate_series(timestamp '2022-01-01', timestamp '2024-12-31', interval 1 day) as g(d)
