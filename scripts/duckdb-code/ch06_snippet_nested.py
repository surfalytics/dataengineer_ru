"""Глава 6. Короткий пример страницы: struct и unnest. Полный разбор: ch06_json.py."""
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
f = lambda n: str(tmp / n)
for title, sql in [
    ("struct: поля по ключу, у Веры location нет", f"""
SELECT name, address['city'] AS city, address['location']['zip'] AS zip
FROM read_ndjson_auto('{f('nested.ndjson')}')"""),
    ("unnest: массив people в строки", f"""
SELECT p['id'] AS id, p['name'] AS name, p['address']['city'] AS city
FROM (SELECT unnest(people) AS p FROM read_json('{f('wrapped.json')}'))"""),
]:
    print(title)
    for row in con.execute(sql).fetchall():
        print("  ", row)
