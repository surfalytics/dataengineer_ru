#!/usr/bin/env python3
"""Chapter 9 (MotherDuck) diagrams. Usage: ch09_diagrams.py [name ...]  (no args = all)
Идеи: рис. 9-5, 9-15..9-18, 9-40..9-42, 9-43 книги + наша схема Dual Execution (см. figures-ch09.md)."""
from excb import N, E, Z, T, run_all

D = {}
GRAY = "#495057"

# ---------- main: local + cloud ----------
D["ch09-architecture"] = dict(items=[
    T("MotherDuck: DuckDB локально и в облаке", 0, -60, 24, "#1971c2"),
    Z("Ваша машина", 0, 0, 430, 330),
    N("loc", "DuckDB\n(CLI, Python, ноутбук)", 60, 60, "p", 310, 100),
    N("file", "Локальные файлы\nCSV, Parquet", 60, 210, "n", 310, 90),
    Z("MotherDuck (AWS)", 640, 0, 460, 330),
    N("web", "Веб-интерфейс:\nSQL-ноутбук", 700, 40, "y", 340, 80),
    N("comp", "Свой изолированный\ncompute у каждого\nпользователя", 700, 150, "g", 340, 100),
    N("db", "my_db, sample_data,\nваши базы и shares", 700, 270, "db", 340, 50),
], edges=[E("loc", "comp", "ATTACH 'md:' + токен"), E("file", "loc")])

# ---------- hierarchy ----------
D["ch09-hierarchy"] = dict(items=[
    T("Имя таблицы: база.схема.таблица", 0, -60, 24, "#1971c2"),
    N("acc", "Аккаунт\nMotherDuck", 0, 100, "n", 200, 100),
    N("my", "my_db\nчтение и запись", 330, -20, "g", 260, 90),
    N("sd", "sample_data\nтолько чтение (share)", 330, 220, "y", 280, 90),
    N("main", "схема main\n(по умолчанию)", 720, -80, "p", 240, 90),
    N("tit", "схема titanic\nCREATE SCHEMA", 720, 50, "p", 240, 90),
    N("t1", "my_db.main.airlines", 1060, -80, "db", 280, 80),
    N("t2", "my_db.titanic.titanic_train", 1060, 50, "db", 330, 80),
], edges=[E("acc", "my"), E("acc", "sd"), E("my", "main"), E("my", "tit"), E("main", "t1"), E("tit", "t2")])

# ---------- share ----------
D["ch09-share"] = dict(items=[
    T("Share: доступ по ссылке, без копий", 0, -60, 24, "#1971c2"),
    N("own", "Владелец:\nmy_db", 0, 80, "g", 220, 100),
    N("sh", "Share (снимок)\nтолько чтение", 520, 80, "y", 260, 100),
    N("u1", "Получатель 1:\nATTACH 'md:_share/...'\nAS my_alias", 940, 0, "p", 330, 110),
    N("u2", "Получатель 2", 940, 180, "p", 330, 80),
    T("Владелец правит базу. Получатели видят правки только после UPDATE SHARE.", 0, 300, 20, GRAY),
], edges=[E("own", "sh", "CREATE SHARE"), E("sh", "u1"), E("sh", "u2")])

# ---------- hybrid ----------
D["ch09-hybrid"] = dict(items=[
    T("Hybrid-запрос: один JOIN, два места данных", 0, -60, 24, "#1971c2"),
    N("fl", "./flights.csv\nна вашем диске", 0, 0, "n", 280, 100),
    N("an", "airlines\nmy_db.main.airlines\nв облаке", 0, 190, "db", 280, 110),
    N("q", "Один запрос:\nJOIN по IATA_CODE\nDual Execution", 480, 90, "y", 300, 110),
    N("res", "Результат:\nрейс + название\nавиакомпании", 980, 90, "g", 280, 110),
    T("Часть работы идёт локально, часть в облаке. Большой файл остаётся у вас.", 0, 340, 20, GRAY),
], edges=[E("fl", "q"), E("an", "q"), E("q", "res")])

if __name__ == "__main__":
    run_all(D)
