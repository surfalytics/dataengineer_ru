{{ config(materialized='table') }}

{{ dbt_utils.date_spine(
    datepart="day",
    start_date="cast('2024-02-01' as date)",
    end_date="cast('2024-04-01' as date)"
) }}
