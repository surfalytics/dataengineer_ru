#!/usr/bin/env python3
"""Chapter 6 (Using DuckDB with JSON Files) diagrams. Usage: ch06_diagrams.py [name ...]  (no args = all)
Идеи: рис. 6-1..6-14 книги, перерисованы по смыслу (см. figures-ch06.md)."""
from excb import N, E, Z, T, run_all

D = {}
GRAY = "#495057"

# ---------- main: three ways ----------
D["ch06-three-ways"] = dict(items=[
    T("Три способа загрузить JSON в DuckDB", 0, -170, 24, "#1971c2"),
    N("f", "JSON-файл", 0, 100, "n", 200, 100),
    N("a", "read_json_auto()\nпервый выбор:\nсхема и формат сами", 380, -60, "g", 300, 120),
    N("b", "read_json()\nавто-определение ошибается:\nformat и columns вручную", 380, 100, "y", 300, 120),
    N("c", "COPY ... FROM\nбольшой файл, простая\nструктура, таблица готова", 380, 260, "pu", 300, 120),
    N("t", "Таблица /\nрезультат запроса", 840, 100, "db", 240, 100),
    T("Читаем сначала первым способом. Остальные нужны, когда он не подходит.", 0, 430, 20, GRAY),
], edges=[E("f", "a"), E("f", "b"), E("f", "c"), E("a", "t"), E("b", "t"), E("c", "t")])

# ---------- redraw: nested JSON -> columns ----------
D["ch06-nested-flow"] = dict(items=[
    T("Как развернуть вложенный JSON в колонки", 0, -60, 24, "#1971c2"),
    N("s1", "Вложенный объект\naddress: {city, location}", 0, 0, "n", 290, 110),
    N("s1b", "Колонка типа struct", 400, 0, "y", 260, 110),
    N("s1c", "address['city']\naddress['location']['zip']", 770, 0, "g", 300, 110),
    N("s2", "Массив в ключе\n{\"people\": [ ... ]}", 0, 200, "n", 290, 110),
    N("s2b", "Одна ячейка\nс массивом", 400, 200, "y", 260, 110),
    N("s2c", "unnest(people) AS p\nстрока на элемент", 770, 200, "pu", 300, 110),
    N("s2d", "p['id'], p['name'],\np['address']['city']", 1180, 200, "g", 290, 110),
    T("Ключ в квадратных скобках или через точку: p.id. Нет поля - будет NULL.", 0, 360, 20, GRAY),
], edges=[E("s1", "s1b"), E("s1b", "s1c"), E("s2", "s2b"), E("s2b", "s2c"), E("s2c", "s2d")])

# ---------- redraw: two JSON layouts + COPY TO ----------
D["ch06-formats"] = dict(items=[
    T("Два вида JSON-файла и экспорт", 0, -60, 24, "#1971c2"),
    N("arr", "format = 'array'\n[ {..}, {..}, {..} ]\nодин массив объектов", 0, 0, "p", 330, 120),
    N("nd", "format = 'newline_delimited'\nодин объект на строку\n(NDJSON)", 0, 190, "g", 330, 120),
    N("tb", "Таблица\nDuckDB", 500, 95, "db", 220, 110),
    N("o1", "COPY t TO 'f.json'\nпо умолчанию NDJSON", 880, 0, "g", 300, 110),
    N("o2", "COPY t TO 'f.json'\n(ARRAY true) - строгий JSON", 880, 190, "p", 300, 110),
], edges=[E("arr", "tb"), E("nd", "tb"), E("tb", "o1"), E("tb", "o2")])

if __name__ == "__main__":
    run_all(D)
