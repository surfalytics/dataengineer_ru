#!/usr/bin/env python3
"""Chapter 4 (data transformation with dbt) diagrams. Usage: ch04_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

# Figs 4-1, 4-2 (own version): where dbt sits in the data flow
D["ch04-dbt-data-flow"] = dict(items=[
    N("git", "Git / GitHub:\nкод проекта", 330, 0, "n", 260, 110),
    N("dbt", "dbt Cloud или dbt Core:\nmodels, tests,\ndocs, jobs", 860, 0, "p", 320, 120),
    N("src", "Исходные системы:\nприложения,\nплатежи, файлы", 0, 330, "n", 240, 110),
    N("el", "EL-инструмент:\nизвлекает\nи загружает", 330, 330, "y", 240, 110),
    N("zone", "", 660, 290, "n", 760, 240),
    T("Платформа данных: BigQuery, Snowflake, Databricks, Redshift", 690, 470, 20, "#495057"),
    N("raw", "Сырые таблицы\n(source)", 700, 330, "db", 280, 110),
    N("mart", "Модели:\nstaging, intermediate,\nmarts", 1100, 330, "g", 280, 110),
    N("bi", "BI, отчёты,\nаналитики", 1520, 330, "pu", 240, 110),
], edges=[E("src", "el"), E("el", "raw"), E("raw", "mart"), E("mart", "bi"),
          E("raw", "dbt", "читает"), E("dbt", "mart", "создаёт"),
          E("git", "dbt", "версии кода", dashed=True)])

# Figs 4-37, 4-39, 4-53 (own version): lineage of the chapter project
D["ch04-lineage"] = dict(items=[
    Z("Sources", -20, -80, 340, 620), Z("Staging", 380, -80, 360, 620),
    Z("Intermediate", 800, -80, 360, 620), Z("Marts и seed", 1220, -80, 320, 620),
    Z("Analyses", 1600, -80, 380, 620),
    N("s1", "jaffle_shop.\ncustomers", 0, 0, "db", 300, 100),
    N("s2", "jaffle_shop.\norders", 0, 170, "db", 300, 100),
    N("s3", "stripe.\npayment", 0, 340, "db", 300, 100),
    N("g1", "stg_jaffle_shop_\ncustomers", 400, 0, "p", 320, 100),
    N("g2", "stg_jaffle_shop_\norders", 400, 170, "p", 320, 100),
    N("g3", "stg_stripe_\norder_payments", 400, 340, "p", 320, 100),
    N("i1", "int_payment_type_\namount_per_order", 820, 340, "y", 320, 100),
    N("dim", "dim_customers", 1240, 0, "g", 280, 100),
    N("fct", "fct_orders", 1240, 170, "g", 280, 100),
    N("seed", "seed_customer_range_\nper_paid_amount", 1240, 400, "q", 280, 100),
    N("a1", "most_valuable_\ncustomers", 1620, 0, "pu", 340, 100),
    N("a2", "customer_range_based_\non_total_paid_amount", 1620, 300, "pu", 340, 100),
    T("+fct_orders: fct_orders и всё, от чего он зависит (левее).   fct_orders+: fct_orders и всё, что зависит от него (правее).",
      0, 580, 20, "#495057"),
], edges=[E("s1", "g1"), E("s2", "g2"), E("s3", "g3"), E("g3", "i1"),
          E("g1", "dim"), E("g2", "fct"), E("i1", "fct"),
          E("dim", "a1"), E("fct", "a1"), E("fct", "a2"), E("seed", "a2")])

# Own diagram (no figure in the book): cascading scope priority of configs
D["ch04-config-cascade"] = dict(items=[
    N("l1", "dbt_project.yml\nstaging: +materialized: view\n(все модели слоя)", 0, 0, "n", 440, 120),
    N("l2", "_jaffle_shop_models.yml\nstg_jaffle_shop_customers:\nmaterialized: table", 0, 240, "y", 440, 120),
    N("l3", "Файл модели .sql\n{{ config(materialized='table') }}", 0, 480, "g", 440, 120),
    N("r1", "stg_jaffle_shop_orders:\nview (из проекта)", 700, 0, "p", 380, 120),
    N("r2", "stg_jaffle_shop_customers:\ntable (из YAML)", 700, 240, "p", 380, 120),
    T("Чем ближе настройка к модели,\nтем выше её приоритет.", 700, 500, 22, "#e03131"),
], edges=[E("l1", "l2", "уточняет"), E("l2", "l3", "уточняет"),
          E("l1", "r1", "по умолчанию"), E("l2", "r2", "перекрывает")])

# Figs 4-54..4-62 (own version): from a dev branch to a scheduled job
D["ch04-deploy-job"] = dict(items=[
    N("dev", "Dev-branch:\nIDE, dev-датасет", 0, 0, "p", 260, 110),
    N("pr", "Pull request:\nобзор кода", 420, 0, "y", 260, 110),
    N("main", "Branch main", 840, 0, "g", 260, 110),
    N("env", "Deployment\nenvironment:\nprod-датасет", 1260, 0, "db", 260, 120),
    N("trig", "Триггер:\nрасписание,\nwebhook или API", 420, 300, "q", 260, 120),
    N("job", "Job: dbt build\n+ docs\n+ source freshness", 840, 300, "pu", 260, 120),
    N("hist", "Run History:\nстатус, шаги,\nлоги", 1260, 300, "n", 260, 120),
], edges=[E("dev", "pr", "commit\nи push"), E("pr", "main", "merge"), E("main", "env"),
          E("trig", "job", "запускает"), E("env", "job", "где и что\nзапускать"),
          E("job", "hist", "результат")])

if __name__ == "__main__":
    run_all(D)
