#!/usr/bin/env python3
"""DDIA2, глава 11 (пакетная обработка). Usage: ch11_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

# own: a distributed batch framework is like an operating system
D["ch11-os-analogy"] = dict(items=[
    T("Одна машина (Unix)", 0, -50, 22, "#1971c2"),
    T("Кластер (распределённая batch-обработка)", 560, -50, 22, "#1971c2"),
    N("u1", "Файловая система ОС\next4, XFS, page cache", 0, 0, "db", 380, 100),
    N("u2", "Ядро ОС: планировщик\nпроцессов, CPU и память", 0, 160, "p", 380, 100),
    N("u3", "Программы и pipes:\nawk | sort | uniq", 0, 320, "q", 380, 100),
    N("d1", "DFS или object store:\nHDFS, S3. Блоки и реплики\nна многих машинах", 560, 0, "db", 460, 100),
    N("d2", "Оркестратор: Kubernetes, YARN.\nScheduler, resource manager,\nexecutor на каждом узле", 560, 160, "p", 460, 100),
    N("d3", "Batch jobs и workflow:\nSpark, Flink, SQL-движки.\nAirflow, Dagster, Prefect", 560, 320, "q", 460, 100),
], edges=[E("u1", "d1"), E("u2", "d2"), E("u3", "d3")])

# Figure 11-1: MapReduce job with three mappers and three reducers
D["ch11-mapreduce"] = dict(items=[
    T("Вход в DFS", 0, -60, 20, "#1971c2"), T("Map tasks", 300, -60, 20, "#1971c2"),
    T("Shuffle: файлы по reducer", 610, -60, 20, "#1971c2"),
    T("Reduce tasks", 950, -60, 20, "#1971c2"), T("Выход в DFS", 1290, -60, 20, "#1971c2"),
    N("i1", "shard m1", 0, 0, "db", 200, 90),
    N("i2", "shard m2", 0, 170, "db", 200, 90),
    N("i3", "shard m3", 0, 340, "db", 200, 90),
    N("m1", "Mapper 1:\nключ и значение,\nсортировка", 300, 0, "q", 240, 90),
    N("m2", "Mapper 2:\nключ и значение,\nсортировка", 300, 170, "q", 240, 90),
    N("m3", "Mapper 3:\nключ и значение,\nсортировка", 300, 340, "q", 240, 90),
    N("r1", "Reducer 1:\nmergesort файлов,\nвызов по ключу", 950, 0, "pu", 240, 90),
    N("r2", "Reducer 2:\nmergesort файлов,\nвызов по ключу", 950, 170, "pu", 240, 90),
    N("r3", "Reducer 3:\nmergesort файлов,\nвызов по ключу", 950, 340, "pu", 240, 90),
    N("o1", "shard r1", 1290, 0, "g", 200, 90),
    N("o2", "shard r2", 1290, 170, "g", 200, 90),
    N("o3", "shard r3", 1290, 340, "g", 200, 90),
    T("Mapper пишет отдельный файл для каждого reducer: hash(ключ) выбирает файл.\n"
      "Файл (m1, r2) — данные mapper 1 для reducer 2. Одинаковые ключи попадают к одному reducer.",
      0, 470, 18, "#495057"),
], edges=[E("i1", "m1"), E("i2", "m2"), E("i3", "m3"),
          E("m1", "r1"), E("m1", "r2"), E("m1", "r3"),
          E("m2", "r1"), E("m2", "r2"), E("m2", "r3"),
          E("m3", "r1"), E("m3", "r2"), E("m3", "r3"),
          E("r1", "o1"), E("r2", "o2"), E("r3", "o3")])

# Figures 11-2 and 11-3: sort-merge join of activity events and user profiles
D["ch11-joins"] = dict(items=[
    N("ev", "События активности\n(fact table):\nuser_id, url, время", 0, 0, "p", 260, 110),
    N("us", "Пользователи\n(dimension):\nuser_id, дата рождения", 0, 200, "db", 260, 110),
    N("me", "Mapper событий:\nключ = user_id,\nзначение = url", 340, 0, "q", 260, 110),
    N("mu", "Mapper пользователей:\nключ = user_id,\nзначение = дата", 340, 200, "q", 260, 110),
    N("sh", "Shuffle по user_id\n+ secondary sort:\nсначала профиль,\nпотом события", 680, 90, "pu", 260, 130),
    N("rd", "Reducer:\nзапоминает дату,\nвыводит url + дата\nдля каждого события", 1020, 90, "y", 260, 130),
    N("nx", "Следующий job:\nключ = url,\nпросмотры по\nвозрастным группам", 1360, 90, "g", 260, 130),
], edges=[E("ev", "me"), E("us", "mu"), E("me", "sh"), E("mu", "sh"),
          E("sh", "rd"), E("rd", "nx")])

# own, 2nd ed. text: MapReduce workflow vs dataflow engine
D["ch11-dataflow"] = dict(items=[
    Z("MapReduce: workflow из отдельных jobs", -20, -60, 1800, 200),
    N("a0", "DFS:\nвходные данные", 0, 0, "db", 220, 100),
    N("a1", "Job 1:\nmap + sort\n+ reduce", 380, 0, "q", 220, 100),
    N("a2", "DFS: промежуточные\nфайлы, реплики\nна дисках", 760, 0, "r", 220, 100),
    N("a3", "Job 2:\nmap + sort\n+ reduce", 1140, 0, "q", 220, 100),
    N("a4", "DFS:\nрезультат", 1520, 0, "db", 220, 100),
    Z("Dataflow engine (Spark, Flink): весь workflow — один job", -20, 200, 1800, 200),
    N("b0", "DFS:\nвходные данные", 0, 260, "db", 220, 100),
    N("b1", "Оператор:\nmap + filter\nв одной task", 380, 260, "q", 220, 100),
    N("b2", "Оператор:\njoin или\ngroup by", 760, 260, "q", 220, 100),
    N("b3", "Оператор:\nагрегация", 1140, 260, "q", 220, 100),
    N("b4", "DFS:\nрезультат", 1520, 260, "db", 220, 100),
    T("Между операторами данные лежат в памяти или на локальном диске. Sort — только там, где он нужен.\n"
      "Потеря данных при сбое: Spark пересчитывает их по истории вычисления, Flink восстанавливает из checkpoint.",
      0, 430, 18, "#495057"),
], edges=[E("a0", "a1"), E("a1", "a2"), E("a2", "a3"), E("a3", "a4"),
          E("b0", "b1"), E("b1", "b2", "память"), E("b2", "b3", "память"), E("b3", "b4")])

if __name__ == "__main__":
    run_all(D)
