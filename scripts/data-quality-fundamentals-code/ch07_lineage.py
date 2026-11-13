"""Глава 7: lineage на уровне полей из SQL моделей.
Парсер SQL берём готовый: функция DuckDB json_serialize_sql отдаёт дерево запроса (AST).
Мы обходим дерево и строим связи «поле-приёмник <- поле-источник».
Два вида связей, как в книге:
  select      - поле источника входит в SELECT и задаёт значение поля-приёмника
  non-select  - поле стоит в WHERE, JOIN, GROUP BY, HAVING: оно меняет набор строк
Запуск: python3 -I scripts/data-quality-fundamentals-code/ch07_lineage.py
Нужны: Python 3 (только стандартная библиотека) и DuckDB CLI в PATH."""
import hashlib
import json
import subprocess

# Таблицы, которые лежат в хранилище до наших моделей (схемы известны)
SOURCES = {
    "raw.orders": ["order_id", "customer_id", "amount", "status", "created_at"],
    "raw.customers": ["customer_id", "email", "country"],
}

# Модели по порядку: staging -> mart -> BI. Модель = готовая таблица из SELECT
MODELS = {
    "staging.paid_orders": """
        SELECT o.order_id, o.customer_id, o.amount
        FROM raw.orders o
        WHERE o.status = 'paid'""",
    "mart.revenue_by_country": """
        WITH enriched AS (
            SELECT c.country, p.amount
            FROM staging.paid_orders p
            JOIN raw.customers c ON c.customer_id = p.customer_id
        )
        SELECT country, SUM(amount) AS revenue
        FROM enriched
        GROUP BY country""",
    "mart.top_customers": """
        SELECT c.email, SUM(p.amount) AS total
        FROM staging.paid_orders p
        JOIN raw.customers c ON c.customer_id = p.customer_id
        GROUP BY c.email""",
    "bi.revenue_dashboard": "SELECT country, revenue FROM mart.revenue_by_country",
    "bi.top_customers_dashboard": "SELECT email, total FROM mart.top_customers",
}


def parse(sql):
    """SQL -> дерево запроса. Парсит сам DuckDB."""
    q = "SELECT json_serialize_sql('" + sql.replace("'", "''") + "') AS j"
    r = subprocess.run(["duckdb", "-json", ":memory:", "-c", q], capture_output=True, text=True, check=True)
    res = json.loads(r.stdout)[0]["j"]
    if isinstance(res, str):
        res = json.loads(res)
    if res["error"]:
        raise ValueError(res["error_message"])
    return res["statements"][0]["node"]


def column_refs(expr):
    """Все ссылки на колонки внутри выражения (в любой глубине)."""
    if isinstance(expr, dict):
        if expr.get("class") == "SUBQUERY":
            raise NotImplementedError("подзапрос внутри выражения")
        if expr.get("class") == "COLUMN_REF":
            yield expr["column_names"]
            return
        for v in expr.values():
            yield from column_refs(v)
    elif isinstance(expr, list):
        for v in expr:
            yield from column_refs(v)


def table_rel(name, known):
    """Реальная таблица как набор колонок: колонка -> (select-источники, non-select-источники)."""
    if name not in known:
        raise ValueError(f"неизвестная таблица {name}")
    return {c: ({(name, c)}, set()) for c in known[name]}


def add_source(frm, ctes, known, scope, conds):
    """Разбираем FROM: заполняем scope (псевдоним -> колонки) и собираем условия JOIN."""
    kind = frm["type"]
    if kind == "EMPTY":
        return
    if kind == "BASE_TABLE":
        short = frm["table_name"]
        full = frm["schema_name"] + "." + short if frm["schema_name"] else short
        rel = ctes[full] if full in ctes else table_rel(full, known)
        for key in (frm["alias"] or short, full):
            scope[key] = rel
    elif kind == "SUBQUERY":
        scope[frm["alias"]] = analyze(frm["subquery"]["node"], ctes, known)
    elif kind == "JOIN":
        if frm["using_columns"]:
            raise NotImplementedError("JOIN ... USING")
        add_source(frm["left"], ctes, known, scope, conds)
        add_source(frm["right"], ctes, known, scope, conds)
        conds.append(frm["condition"])
    else:
        raise NotImplementedError("источник FROM типа " + kind)


def resolve(names, scope):
    """Ссылка на колонку -> (select-источники, non-select-источники) реальных таблиц."""
    col = names[-1]
    if len(names) > 1:
        key = ".".join(names[:-1])
        if key not in scope or col not in scope[key]:
            raise ValueError("не найдена колонка " + ".".join(names))
        return scope[key][col]
    rels = list({id(r): r for r in scope.values()}.values())
    hits = [r for r in rels if col in r]
    if len(hits) != 1:
        raise ValueError(f"колонка {col} найдена в {len(hits)} источниках, напишите псевдоним")
    return hits[0][col]


def analyze(node, ctes, known):
    """Узел запроса -> {имя колонки результата: (select-источники, non-select-источники)}."""
    if node["modifiers"]:
        raise NotImplementedError("ORDER BY, LIMIT, DISTINCT")
    ctes = dict(ctes)
    for item in node["cte_map"]["map"]:
        ctes[item["key"]] = analyze(item["value"]["query"]["node"], ctes, known)
    if node["type"] == "SET_OPERATION_NODE":
        left = analyze(node["left"], ctes, known)
        right = analyze(node["right"], ctes, known)
        if len(left) != len(right):
            raise ValueError("в UNION разное число колонок")
        return {name: (s1 | s2, n1 | n2)
                for (name, (s1, n1)), (_, (s2, n2)) in zip(left.items(), right.items())}
    if node["type"] != "SELECT_NODE":
        raise NotImplementedError(node["type"])

    scope, conds = {}, []
    add_source(node["from_table"], ctes, known, scope, conds)
    # поля из JOIN, WHERE, GROUP BY, HAVING меняют набор строк всех колонок результата
    non = set()
    for expr in conds + [node["where_clause"], node["having"]] + node["group_expressions"]:
        for names in column_refs(expr):
            sel_part, non_part = resolve(names, scope)
            non |= sel_part | non_part
    out = {}
    for item in node["select_list"]:
        if item["class"] == "STAR":
            raise NotImplementedError("SELECT *")
        sel, extra = set(), set()
        for names in column_refs(item):
            sel_part, non_part = resolve(names, scope)
            sel |= sel_part
            extra |= non_part
        name = item["alias"] or (item["column_names"][-1] if item["class"] == "COLUMN_REF" else "")
        if not name:
            raise ValueError("выражению нужен псевдоним (AS ...)")
        out[name] = (sel, extra | non)
    return out


def build_edges(models=MODELS, sources=SOURCES):
    """Все модели -> плоский список связей и записи в стиле примера 7-1 из книги."""
    known = {k: list(v) for k, v in sources.items()}
    edges, records = [], []
    for dest, sql in models.items():
        rel = analyze(parse(sql), {}, known)
        known[dest] = list(rel)
        for col, (sel, non) in rel.items():
            sel_list = sorted(sel)
            non_list = sorted(non - sel)
            for t, c in sel_list:
                edges.append((dest, col, t, c, "select"))
            for t, c in non_list:
                edges.append((dest, col, t, c, "non-select"))
            body = {"destination_table": dest, "destination_field": col,
                    "sources": [{"table": t, "field": c} for t, c in sel_list],
                    "non_select_sources": [{"table": t, "field": c} for t, c in non_list]}
            # id документа = таблица + хэш объекта lineage (идея книги)
            digest = hashlib.sha1(json.dumps(body, sort_keys=True).encode()).hexdigest()[:10]
            records.append({"edge_id": f"{dest}:{digest}", **body})
    return edges, records


if __name__ == "__main__":
    edges, records = build_edges()
    print("== 1. Связи, найденные в 5 моделях")
    print("всего связей:", len(edges))
    print("из них select:", sum(1 for e in edges if e[4] == "select"),
          "| non-select:", sum(1 for e in edges if e[4] == "non-select"))

    print("\n== 2. Запись lineage для поля mart.revenue_by_country.revenue")
    rec = next(r for r in records if r["destination_table"] == "mart.revenue_by_country"
               and r["destination_field"] == "revenue")
    fmt = lambda items: ", ".join(f"{i['table']}.{i['field']}" for i in items)
    print("edge_id:", rec["edge_id"])
    print(f"поле: {rec['destination_table']}.{rec['destination_field']}")
    print("sources (select):", fmt(rec["sources"]))
    print("non_select_sources:", fmt(rec["non_select_sources"]))

    print("\n== 3. Парсер не молчит, если не умеет разобрать запрос")
    risky = "SELECT o.order_id FROM raw.orders o WHERE o.customer_id IN (SELECT c.customer_id FROM raw.customers c)"
    try:
        analyze(parse(risky), {}, {k: list(v) for k, v in SOURCES.items()})
    except NotImplementedError as exc:
        print("не поддерживается:", exc)
