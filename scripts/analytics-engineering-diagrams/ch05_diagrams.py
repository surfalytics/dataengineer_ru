#!/usr/bin/env python3
"""Chapter 5 (dbt advanced topics) diagrams. Usage: ch05_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

# Fig 5-1 (lineage) + Fig 5-2..5-4 (table, view, ephemeral) + incremental and materialized view
D["ch05-materializations"] = dict(items=[
    T("Lineage dim_customers и пять способов построить staging-модель", 0, -60, 22, "#1971c2"),
    N("src", "source\njaffle_shop.customers", 150, 0, "n", 300, 90),
    N("stg", "stg_jaffle_shop_customers", 600, 0, "p", 330, 90),
    N("dim", "dim_customers", 1080, 0, "g", 300, 90),
    Z("Какую materialization выбрать для stg_jaffle_shop_customers", 0, 170, 1560, 260),
    N("tb", "table\nданные лежат на диске:\nчитать быстро,\nстроить долго", 20, 230, "db", 280, 170),
    N("vw", "view\nхранится только запрос:\nданные считаются\nпри каждом чтении", 330, 230, "p", 280, 170),
    N("ep", "ephemeral\nв базе объекта нет:\nкод встраивается\nкак CTE ниже", 640, 230, "pu", 280, 170),
    N("inc", "incremental\nпри каждом запуске\nдобавляет новые\nи изменённые строки", 950, 230, "y", 280, 170),
    N("mv", "materialized view\nрезультат хранится,\nплатформа сама\nего обновляет", 1260, 230, "g", 280, 170),
], edges=[E("src", "stg"), E("stg", "dim")])

# own: incremental run with merge strategy (Example 5-1, 5-2)
D["ch05-incremental-merge"] = dict(items=[
    T("Как работает incremental-модель со стратегией merge", 0, -60, 22, "#1971c2"),
    N("src", "source orders\nвсе строки\nисточника", 0, 0, "n", 260, 110),
    N("chk", "is_incremental()?\nмодель уже есть\nи нет --full-refresh", 420, 0, "y", 300, 110),
    N("flt", "where _etl_loaded_at >=\nmax(_etl_loaded_at)\nиз {{ this }}", 880, 0, "pu", 300, 110),
    N("mrg", "merge\nпо unique_key\norder_id", 1340, 0, "p", 260, 110),
    N("full", "Первый запуск:\nстроим всю таблицу\nиз источника", 420, 260, "n", 300, 110),
    N("upd", "order_id уже есть:\nстрока обновляется", 1060, 260, "g", 260, 110),
    N("ins", "order_id новый:\nстрока добавляется", 1400, 260, "g", 260, 110),
], edges=[E("src", "chk"), E("chk", "flt", "да"), E("flt", "mrg"), E("chk", "full", "нет"),
          E("mrg", "upd"), E("mrg", "ins")])

# own: macros reuse chain (Example 5-7, 5-11..5-15)
D["ch05-macros-reuse"] = dict(items=[
    T("Макросы: один общий запрос, много вызовов", 0, -60, 22, "#1971c2"),
    N("tbl", "stg_stripe_order_payments", 0, 0, "db", 320, 90),
    N("gcv", "get_column_values(\ncolumn_name, table_name)\nrun_query + select distinct", 520, -10, "pu", 380, 110),
    N("gpt", "get_payment_types()\n['cash', 'credit', ...]", 360, 220, "pu", 320, 100),
    N("gpm", "get_payment_methods()\n['bank_transfer', 'cash', ...]", 780, 220, "pu", 360, 100),
    N("mdl", "int_payment_type_\namount_per_order\n{% for %} по списку", 360, 440, "p", 320, 120),
    N("sql", "SQL после компиляции:\nсумма по каждому типу,\nпо столбцу на тип", 900, 440, "g", 320, 120),
], edges=[E("gcv", "tbl", "запрос"), E("gcv", "gpt"), E("gcv", "gpm"), E("gpt", "mdl", "список"),
          E("mdl", "sql", "dbt compile")])

# own: semantic layer flow (Example 5-22..5-24)
D["ch05-semantic-layer"] = dict(items=[
    T("dbt semantic layer: от модели к готовому запросу", 0, -60, 22, "#1971c2"),
    N("fct", "fct_orders\nmart-модель", 0, 0, "db", 280, 120),
    N("sem", "Semantic model orders\nentities: order_id, customer\ndimensions: order_date, ...\nmeasures: total_amount, ...", 420, -20, "p", 400, 160),
    N("met", "Metrics\norder_total\norder_count\ncompleted_orders", 960, -10, "g", 300, 140),
    N("mf", "MetricFlow\nсемантический движок\nmf query --metrics ...", 960, 270, "pu", 300, 130),
    N("sql", "Сгенерированный SQL\nSELECT SUM(total_amount)\nFROM fct_orders", 480, 270, "y", 320, 130),
    N("usr", "Аналитики, BI, API:\nодна метрика,\nодно определение", 0, 270, "n", 280, 130),
], edges=[E("fct", "sem"), E("sem", "met"), E("met", "mf"), E("mf", "sql"), E("sql", "usr")])

if __name__ == "__main__":
    run_all(D)
