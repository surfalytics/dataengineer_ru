#!/usr/bin/env python3
"""Chapter 7 (end-to-end lineage) diagrams. Usage: ch07_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

# main: lineage as a map from source to dashboard
D["ch07-lineage-map"] = dict(items=[
    T("Источники", 0, -50, 22, "#1971c2"), T("Staging", 350, -50, 22, "#1971c2"),
    T("Mart", 700, -50, 22, "#1971c2"), T("BI-слой", 1050, -50, 22, "#1971c2"),
    N("o", "raw.orders\nполе status\nизменилось", 0, 0, "r", 270, 120),
    N("c", "raw.customers", 0, 250, "n", 270, 90),
    N("p", "staging.paid_orders", 350, 0, "p", 270, 100),
    N("m", "mart.\nrevenue_by_country", 700, 100, "p", 270, 110),
    N("b", "bi.revenue_dashboard\nвыручка выглядит\nстранно", 1050, 100, "y", 300, 120),
    N("up", "Вверх (upstream): откуда пришла цифра?\nЭто поиск root cause", 350, 330, "g", 400, 100),
    N("dn", "Вниз (downstream): что заденет поломка?\nЭто оценка impact", 840, 330, "g", 420, 100),
], edges=[E("o", "p"), E("p", "m"), E("c", "m"), E("m", "b")])

# fig 7-3 + 7-4: field-level lineage, select and non-select
D["ch07-field-level"] = dict(items=[
    Z("Источники (поля)", -20, -70, 380, 640),
    N("s1", "staging.paid_orders\n.amount", 0, 0, "g", 340, 100),
    N("s2", "raw.customers\n.country", 0, 150, "y", 340, 100),
    N("s3", "raw.customers\n.customer_id", 0, 300, "y", 340, 100),
    N("s4", "staging.paid_orders\n.customer_id", 0, 450, "y", 340, 100),
    N("d", "mart.revenue_by_country\n.revenue\n= SUM(amount)", 640, 215, "p", 340, 130),
    N("b", "bi.revenue_dashboard\n.revenue", 1180, 230, "pu", 300, 100),
    N("l1", "Зелёный: поле входит в SELECT.\nЕго изменение меняет значение revenue.", 0, 600, "g", 560, 90),
    N("l2", "Жёлтый: поле в JOIN или GROUP BY.\nОно меняет набор строк, но не само значение.", 620, 600, "y", 600, 90),
], edges=[E("s1", "d", "SELECT"), E("s2", "d", "GROUP BY", dashed=True),
          E("s3", "d", "JOIN", dashed=True), E("s4", "d", "JOIN", dashed=True), E("d", "b")])

# own + fig 7-3: how to build lineage
D["ch07-lineage-design"] = dict(items=[
    N("q", "SQL запросов\nи моделей\n(query log, dbt)", 0, 0, "n", 270, 120),
    N("pr", "Парсер (ANTLR):\nSQL в дерево\nзапроса", 340, 0, "pu", 270, 120),
    N("rs", "Разбор колонок:\nпсевдонимы, WITH,\nподзапросы до\nреальных таблиц", 680, 0, "pu", 270, 120),
    N("ed", "Связи (edges):\nполе-приёмник\n← поля-источники", 1020, 0, "g", 270, 120),
    N("st", "Хранилище lineage:\nid = таблица +\nхэш объекта", 1020, 230, "db", 270, 120),
    N("qr", "Запросы:\nimpact, root cause,\nPII, data debt", 680, 230, "p", 270, 120),
    N("ui", "UI: BI-слой и\nисточники сверху,\nдетали по клику", 340, 230, "y", 270, 120),
    N("rk", "Риск: сотни комбинаций\nSQL. Прототип покрыл\nоколо 70%. Тестируйте\nкаждый clause", 0, 230, "r", 270, 130),
], edges=[E("q", "pr"), E("pr", "rs"), E("rs", "ed"), E("ed", "st"), E("st", "qr"), E("qr", "ui")])

# fig 7-6 + case study: Fox
D["ch07-fox-platform"] = dict(items=[
    N("src", "Больше 200\nисточников:\nbatch, micro-batch,\nstream", 0, 80, "n", 250, 150),
    Z("Lakehouse: «трёхслойный пирог»", 320, -30, 880, 470),
    N("raw", "Raw\nданные как\nпришли", 350, 40, "n", 240, 140),
    N("opt", "Optimized\nотсортированы,\nбыстрые форматы.\nПул для self-serve", 650, 40, "db", 270, 140),
    N("pub", "Published\nмодели данных\nи отчёты", 960, 40, "g", 210, 140),
    N("obs", "Data observability: QA, validation, alerting и автоматический lineage\nна всём стеке", 350, 250, "pu", 820, 100),
    N("usr", "Аналитики и\nпродукты данных:\nself-serve\nи ad hoc", 1260, 80, "g", 250, 150),
    N("ctl", "Controlled freedom: центральная команда держит приём данных, безопасность\nи стандартные executive-отчёты. Всё остальное пользователи делают сами.", 0, 500, "y", 1510, 90),
], edges=[E("src", "raw"), E("raw", "opt"), E("opt", "pub"), E("pub", "usr")])

if __name__ == "__main__":
    run_all(D)
