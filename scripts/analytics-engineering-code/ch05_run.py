#!/usr/bin/env python3
"""Глава 5: запускает проект ch05_dbt на DuckDB в два прогона и печатает результаты для страницы.
Прогон 1: исходные заказы. Потом меняем источник: заказ 3 меняет статус, появляются заказ 5
и новый тип оплаты gift_card. Прогон 2: incremental merge, snapshot, макросы подхватывают изменения.
Запуск: <venv>/bin/python -I scripts/analytics-engineering-code/ch05_run.py
Venv: pip install -r scripts/analytics-engineering-code/requirements-ch05.txt (сеть нужна для dbt deps)"""
import shutil, subprocess, sys
from pathlib import Path
import duckdb

PROJ = Path(__file__).resolve().parent / "ch05_dbt"
DB = PROJ / "ch05.duckdb"
DBT = str(Path(sys.executable).parent / "dbt")

BATCH1 = """
create schema raw;
create table raw.customers as
select * from (values (1, 'Anna', 'Ivanova'), (2, 'Boris', 'Petrov'), (3, 'Vera', 'Smirnova'))
    t(id, first_name, last_name);
create table raw.orders as
select id, user_id, order_date::date as order_date, status,
       timestamp '2024-03-01 08:00' as _etl_loaded_at
from (values (1, 1, '2024-02-27', 'completed'), (2, 2, '2024-02-28', 'completed'),
             (3, 1, '2024-02-29', 'placed'),    (4, 3, '2024-03-01', 'placed'))
    t(id, user_id, order_date, status);
create table raw.payments as
select * from (values
    (1, 1, 'cash',          'cash',   'success', 10.00),
    (2, 1, 'credit_card',   'credit', 'success', 15.00),
    (3, 2, 'credit_card',   'credit', 'fail',    20.00),
    (4, 2, 'credit_card',   'credit', 'success', 20.00),
    (5, 3, 'bank_transfer', 'credit', 'success', 30.00),
    (6, 4, 'cash',          'cash',   'success',  0.00)
) t(id, order_id, payment_method, payment_type, status, amount);
"""

BATCH2 = """
update raw.orders set status = 'shipped', _etl_loaded_at = timestamp '2024-03-02 08:00' where id = 3;
insert into raw.orders values (5, 2, date '2024-03-02', 'placed', timestamp '2024-03-02 08:00');
insert into raw.payments values (7, 5, 'gift_card', 'gift_card', 'success', 25.00);
"""


def dbt(*args):
    r = subprocess.run([DBT, *args, "--profiles-dir", str(PROJ), "--project-dir", str(PROJ)],
                       cwd=PROJ, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"dbt {' '.join(args)} failed:\n{r.stdout[-3000:]}\n{r.stderr[-2000:]}")
    return r.stdout


def sql(script):
    with duckdb.connect(str(DB)) as con:
        con.execute(script)


def table(name, query):
    with duckdb.connect(str(DB)) as con:
        cur = con.execute(query)
        cols = [d[0] for d in cur.description]
        rows = [["NULL" if v is None else str(v) for v in r] for r in cur.fetchall()]
    w = [max(len(c), *(len(r[i]) for r in rows)) for i, c in enumerate(cols)]
    print(f"=== {name} ===")
    print("  ".join(c.ljust(w[i]) for i, c in enumerate(cols)).rstrip())
    for r in rows:
        print("  ".join(v.ljust(w[i]) for i, v in enumerate(r)).rstrip())


def compiled(name, rel_path, start=None):
    text = (PROJ / "target/compiled/ch05_jaffle" / rel_path).read_text().strip("\n")
    lines = [l.rstrip() for l in text.splitlines()]
    if start:
        lines = lines[next(i for i, l in enumerate(lines) if l.strip() == start):]
    out, blank = [], False
    for l in lines:  # схлопываем подряд идущие пустые строки, которые оставляет Jinja
        if not l.strip():
            if blank: continue
            blank = True
        else:
            blank = False
        out.append(l)
    print(f"=== {name} ===")
    print("\n".join(out))


DB.unlink(missing_ok=True)
shutil.rmtree(PROJ / "target", ignore_errors=True)
if not (PROJ / "dbt_packages/dbt_utils").exists():
    dbt("deps")
sql(BATCH1)
dbt("parse")                      # проверяет и семантическую модель с метриками
dbt("build", "--target", "deploy")
table("run1_orders", "select * from main.stg_jaffle_shop_orders order by order_id")

sql(BATCH2)
dbt("build", "--target", "deploy")
table("run2_orders", "select * from main.stg_jaffle_shop_orders order by order_id")
table("snapshot", """select id, status, dbt_valid_from, dbt_valid_to
                     from snapshots.orders_status_snapshot order by id, dbt_valid_from""")
table("payments_pivot", "select * from main.int_payment_type_amount_per_order order by order_id")
compiled("pivot_compiled", "models/intermediate/int_payment_type_amount_per_order.sql", "select")
table("cash_share", "select * from main.fct_orders_cash_share order by order_id")
table("time_spine", "select count(*) as days, min(date_day)::date as first_day, max(date_day)::date as last_day from main.metricflow_time_spine")

dbt("compile", "-s", "fct_orders", "--target", "dev")
compiled("fct_dev", "models/marts/fct_orders.sql", "from orders as ord")
dbt("compile", "-s", "fct_orders", "--target", "deploy")
compiled("fct_deploy", "models/marts/fct_orders.sql", "from orders as ord")
dbt("compile", "-s", "dim_customers")
compiled("dim_ephemeral", "models/marts/dim_customers.sql")
out = dbt("--quiet", "compile", "--inline", "{{ sum_two_values(13, 89) }}")
print("=== sum_inline ===")
print(out.strip())


def mf(*args):  # MetricFlow: семантический движок dbt
    import os
    r = subprocess.run([str(Path(DBT).parent / "mf"), "query", *args], cwd=PROJ, capture_output=True, text=True,
                       env={**os.environ, "DBT_PROFILES_DIR": str(PROJ), "NO_COLOR": "1"})
    if r.returncode != 0:
        raise SystemExit(f"mf {' '.join(args)} failed:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}")
    return [l.rstrip() for l in r.stdout.splitlines()]


lines = mf("--metrics", "order_total", "--explain")
print("=== mf_explain ===")
print("\n".join(l for l in lines[next(i for i, l in enumerate(lines) if l.startswith("SELECT")):] if l.strip()))
print("=== mf_values ===")
print("\n".join([l for l in mf("--metrics", "order_total,order_count,completed_orders") if l.strip()][-3:]))
