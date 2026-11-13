"""Глава 6. JSON в DuckDB: read_json_auto, read_json, struct, unnest, несколько файлов, COPY.
JSON-файлы строим сами во временной папке. Данные фиксированные."""
import json
import tempfile
from pathlib import Path

import duckdb

tmp = Path(tempfile.mkdtemp(prefix="duck_ch6_"))
people = [
    {"id": 1, "name": "Анна", "address": {"city": "Москва", "location": {"zip": 101000}}, "weight": 61.5},
    {"id": 2, "name": "Борис", "address": {"city": "Казань", "location": {"zip": 420000}}, "weight": 80.0},
    {"id": 3, "name": "Вера", "address": {"city": "Тверь"}, "weight": 55.25},  # у Веры нет location
]
flat = [{k: v for k, v in p.items() if k != "address"} for p in people]
(tmp / "flat.json").write_text(json.dumps(flat))
(tmp / "nested.ndjson").write_text("\n".join(json.dumps(p) for p in people))
(tmp / "wrapped.json").write_text(json.dumps({"people": people}))
(tmp / "day1.json").write_text(json.dumps([{"id": 1, "city": "Москва", "temp": 3}]))
(tmp / "day2.json").write_text(json.dumps([{"id": 2, "city": "Казань", "temp": "холодно"}]))

con = duckdb.connect()


def show(title, sql):
    print(title)
    for row in con.execute(sql).fetchall():
        print("  ", row)


f = lambda n: str(tmp / n)
show("1. read_json_auto: типы колонок", f"DESCRIBE SELECT * FROM read_json_auto('{f('flat.json')}')")
show("2. records = false: объект целиком в одной колонке", f"SELECT * FROM read_json_auto('{f('flat.json')}', records = false)")
show("3. read_json с columns: читаем только id и weight", f"""
    SELECT * FROM read_json('{f('flat.json')}', format = 'array',
        columns = {{id: 'INTEGER', weight: 'FLOAT'}})""")
show("4. NDJSON, вложенный объект как struct", f"DESCRIBE SELECT address FROM read_ndjson_auto('{f('nested.ndjson')}')")
show("5. Поля struct по ключу; у Веры location нет, будет NULL", f"""
    SELECT name, address['city'] AS city, address['location']['zip'] AS zip
    FROM read_ndjson_auto('{f('nested.ndjson')}')""")
show("6. Массив внутри ключа: unnest", f"""
    SELECT p['id'] AS id, p['name'] AS name, p['address']['city'] AS city
    FROM (SELECT unnest(people) AS p FROM read_json('{f('wrapped.json')}'))""")
show("7. Два файла, поле temp: число и строка", f"""
    SELECT * FROM read_json(['{f('day1.json')}', '{f('day2.json')}'])""")
show("8. Тип temp после слияния", f"DESCRIBE SELECT temp FROM read_json(['{f('day1.json')}', '{f('day2.json')}'])")
show("9. Маска day*.json", f"SELECT count(*) AS files_rows FROM read_json('{tmp}/day*.json')")

con.execute("CREATE TABLE people (id INTEGER, name VARCHAR, weight FLOAT)")
con.execute(f"COPY people FROM '{f('flat.json')}' (FORMAT JSON, AUTO_DETECT true)")
show("10. COPY FROM: строк в таблице", "SELECT count(*) AS n FROM people")
con.execute(f"COPY people TO '{f('out.json')}' (FORMAT JSON)")
con.execute(f"COPY people TO '{f('out_array.json')}' (FORMAT JSON, ARRAY true)")
print("11. COPY TO без ARRAY: по объекту на строку")
print((tmp / "out.json").read_text().rstrip())
print("12. COPY TO с ARRAY true: один массив")
print((tmp / "out_array.json").read_text().rstrip())
