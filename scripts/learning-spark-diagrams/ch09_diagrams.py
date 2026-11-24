#!/usr/bin/env python3
"""Chapter 9 (Building Reliable Data Lakes) diagrams. Usage: ch09_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

# Own figure: database -> data lake -> lakehouse (the book has no figure for this idea)
D["ch09-evolution"] = dict(items=[
    N("db", "База данных\n\nтаблицы и SQL\nACID есть\nscale-out дорогой", 0, 0, "db", 320, 190),
    N("dl", "Озеро данных\n\nфайлы в открытых форматах\nscale-out дешёвый\nACID нет", 560, 0, "y", 320, 190),
    N("lh", "Lakehouse\n\nфайлы озера + журнал\nтранзакций\nACID, схема, upsert", 1120, 0, "g", 320, 190),
], edges=[E("db", "dl", "дорого и закрыто"), E("dl", "lh", "нет транзакций")])

# Own figure: Delta Lake transaction log, writers, readers, time travel
D["ch09-delta-log"] = dict(items=[
    N("w1", "Пакетная запись\nappend, MERGE", 0, 0, "p", 260, 100),
    N("w2", "Потоковая запись\nStructured Streaming", 0, 150, "p", 260, 100),
    N("log", "Журнал транзакций\n_delta_log", 420, 75, "q", 280, 100),
    N("files", "Файлы данных\nParquet", 860, 75, "db", 260, 100),
    T("Версии таблицы в журнале", 0, 310, 20, "#e8590c"),
    N("v0", "v0\nWRITE", 0, 360, "y", 200, 100),
    N("v1", "v1\nSTREAMING UPDATE", 260, 360, "y", 200, 100),
    N("v2", "v2\nWRITE", 520, 360, "y", 200, 100),
    N("v3", "v3\nUPDATE", 780, 360, "y", 200, 100),
    N("v4", "v4\nDELETE", 1040, 360, "y", 200, 100),
    N("r1", "Читатель: последняя версия\n(v4)", 920, 560, "g", 320, 100),
    N("r2", "Time travel\nversionAsOf = 1", 160, 560, "pu", 300, 100),
], edges=[E("w1", "log", "commit"), E("w2", "log", "commit"), E("log", "files", "файлы"),
          E("log", "v2", dashed=True),
          E("v0", "v1"), E("v1", "v2"), E("v2", "v3"), E("v3", "v4"),
          E("v4", "r1"), E("v1", "r2")])

# Own figure: schema enforcement and explicit schema evolution
D["ch09-schema"] = dict(items=[
    N("wr", "Запись\nDataFrame", 0, 0, "p", 250, 100),
    N("dec", "Схема совпадает\nс таблицей?", 330, -30, "y", 330, 160, "diamond"),
    N("ok", "Коммит\nв журнал", 800, 0, "g", 300, 100),
    N("err", "AnalysisException\nничего не записано", 330, 280, "r", 330, 100),
    N("ms", "Явно:\nmergeSchema = true", 800, 280, "pu", 300, 100),
    N("res", "Колонка добавлена,\nстарые строки: NULL", 800, 460, "g", 300, 100),
], edges=[E("wr", "dec"), E("dec", "ok", "да"), E("dec", "err", "нет"),
          E("err", "ms", "явно"), E("ms", "res")])

if __name__ == "__main__":
    run_all(D)
