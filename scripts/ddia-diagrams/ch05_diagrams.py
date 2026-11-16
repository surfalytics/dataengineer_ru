#!/usr/bin/env python3
"""DDIA2, chapter 5 (encoding and evolution) diagrams. Usage: ch05_diagrams.py [name ...]  (no args = all)
Reused without sources (1st-edition images): ch05-compatibility, ch05-avro-resolution."""
from excb import N, E, Z, T, run_all

D = {}

# Fig 5-1: old code reads a record of new code, updates it and loses the unknown field
D["ch05-unknown-field"] = dict(items=[
    T("Старый код перезаписывает запись нового кода", 0, -50, 22, "#1971c2"),
    N("v2", "Новый код v2\nдобавил поле photoUrl", 0, 0, "p", 270, 100),
    N("db1", "База:\nuserName, favoriteNumber,\nphotoUrl", 430, 0, "db", 290, 100),
    N("v1", "Старый код v1\nчитает запись в объект\nбез photoUrl", 880, 0, "n", 290, 100),
    N("v1w", "v1 меняет\nfavoriteNumber\nи сохраняет объект", 880, 220, "n", 290, 110),
    N("db2", "База:\nuserName, favoriteNumber\nphotoUrl потерян", 430, 220, "r", 290, 110),
    N("ok", "Правильно: старый код\nхранит неизвестные поля\nи пишет их обратно", 0, 220, "g", 270, 110),
], edges=[E("v2", "db1", "пишет"), E("db1", "v1", "читает"), E("v1", "v1w"),
          E("v1w", "db2", "пишет"), E("db2", "ok", "решение", dashed=True)])

# Our redraw of the 1st-edition data-flow image: four modes of dataflow in DDIA2
D["ch05-data-flow"] = dict(items=[
    T("Четыре пути данных между процессами", 0, -50, 22, "#1971c2"),
    N("a", "Процесс-отправитель\nкодирует данные в байты", 490, 0, "n", 400, 90),
    N("m1", "База данных\nзапись сейчас,\nчтение потом", 0, 200, "db", 300, 110),
    N("m2", "Сервисы: REST и RPC\nзапрос и ответ\nпо сети", 360, 200, "q", 300, 110),
    N("m3", "Workflow engine\nзадачи и\ndurable execution", 720, 200, "y", 300, 110),
    N("m4", "Message broker\nи акторы:\nасинхронные сообщения", 1080, 200, "pu", 300, 110),
    N("r1", "Нужны обе\nсовместимости:\nданные живут\nдольше кода", 0, 400, "r", 300, 140),
    N("r2", "Сначала серверы,\nпотом клиенты:\nbackward для запросов,\nforward для ответов", 360, 400, "r", 300, 140),
    N("r3", "Код задач\nдетерминирован;\nновую версию\nставят рядом со старой", 720, 400, "r", 300, 140),
    N("r4", "Нужны обе\nсовместимости;\nне терять неизвестные\nполя при пересылке", 1080, 400, "r", 300, 140),
], edges=[E("a", "m1"), E("a", "m2"), E("a", "m3"), E("a", "m4"),
          E("m1", "r1", dashed=True), E("m2", "r2", dashed=True), E("m3", "r3", dashed=True),
          E("m4", "r4", dashed=True)])

if __name__ == "__main__":
    run_all(D)
