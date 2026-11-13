"""Глава 6. Короткий пример страницы: два файла с разным типом поля и экспорт. Полный разбор: ch06_json.py."""
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
print("Два файла, поле temp: число и строка")
for row in con.execute(f"SELECT * FROM read_json(['{f('day1.json')}', '{f('day2.json')}'])").fetchall():
    print("  ", row)
print("Тип temp:", con.execute(f"DESCRIBE SELECT temp FROM read_json(['{f('day1.json')}', '{f('day2.json')}'])").fetchone()[1])

con.execute("CREATE TABLE people (id INTEGER, name VARCHAR, weight FLOAT)")
con.execute(f"COPY people FROM '{f('flat.json')}' (FORMAT JSON, AUTO_DETECT true)")
con.execute(f"COPY people TO '{f('out.json')}' (FORMAT JSON)")
con.execute(f"COPY people TO '{f('out_array.json')}' (FORMAT JSON, ARRAY true)")
print("COPY TO без ARRAY:")
print((tmp / "out.json").read_text().rstrip())
print("COPY TO с ARRAY true:")
print((tmp / "out_array.json").read_text().rstrip())
