"""Сверка дневного объёма с семью предыдущими днями. DuckDB 1.3.2."""
import duckdb

QUERY = """
with volumes as (
    select
        max(daily_count) filter (where load_date = current_date) as today,
        avg(daily_count) filter (
            where load_date >= current_date - 7 and load_date < current_date
        ) as baseline
    from daily_row_counts
)
select today, round(baseline, 1),
       case when today is null or baseline is null then 'NO DATA'
            when today < baseline * 0.5 then 'FAIL' else 'PASS' end
from volumes
"""


def main():
    with duckdb.connect() as connection:
        connection.execute("""
            create table daily_row_counts as
            select current_date - cast(i as integer) as load_date,
                   case when i = 0 then 40 else 100 end as daily_count
            from range(8) as days(i)
        """)
        today, baseline, status = connection.execute(QUERY).fetchone()
        print(today, baseline, status)


if __name__ == "__main__":
    main()
