#!/usr/bin/env python3
"""Chapter 8 (Transactions) diagrams. Usage: ch08_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, T, run_all

D = {}

# Table 8-1 as a picture (main diagram): what each isolation level prevents and what is left
D["ch08-isolation-levels"] = dict(items=[
    T("Уровни изоляции: что каждый уровень предотвращает", 0, -60, 24, "#1971c2"),
    N("ru", "Read uncommitted\nнет dirty writes", 0, 0, "n", 330, 120),
    N("rc", "Read committed\n+ нет dirty reads", 390, 0, "db", 330, 120),
    N("si", "Snapshot isolation\n(MVCC)\n+ нет read skew\nlost update: зависит\nот базы", 780, 0, "p", 330, 150),
    N("se", "Serializable\n+ нет lost updates\n+ нет write skew\n+ нет phantoms", 1170, 0, "g", 330, 150),
    N("ru2", "Остаются: dirty reads,\nread skew, lost updates,\nwrite skew", 0, 260, "r", 330, 120),
    N("rc2", "Остаются: read skew,\nlost updates,\nwrite skew", 390, 260, "r", 330, 120),
    N("si2", "Остаются: write skew\nи phantoms в\nread-write транзакциях", 780, 260, "r", 330, 120),
    N("se2", "Цена: скорость\nили abort и retry", 1170, 260, "q", 330, 120),
    T("Названия в базах путаются: repeatable read в PostgreSQL — это snapshot isolation,\n"
      "в MySQL — более слабый уровень, в Db2 — serializable. «Serializable» в Oracle — snapshot isolation.",
      0, 430, 18),
], edges=[E("ru", "rc"), E("rc", "si"), E("si", "se"),
          E("ru", "ru2", dashed=True), E("rc", "rc2", dashed=True),
          E("si", "si2", dashed=True), E("se", "se2", dashed=True)])

# Fig 8-8: write skew with two doctors on call
D["ch08-write-skew"] = dict(items=[
    T("Write skew: два врача уходят с дежурства одновременно", 0, -110, 24, "#e03131"),
    T("Обе транзакции читают один snapshot смены 1234", 0, -55, 18),
    N("a1", "Aaliyah: SELECT count(*)\nвидит 2 врача on_call", 0, 0, "p", 480, 100),
    N("b1", "Bryce: SELECT count(*)\nвидит 2 врача on_call", 720, 0, "p", 480, 100),
    N("a2", "Aaliyah: UPDATE своей строки\non_call = false", 0, 200, "q", 480, 100),
    N("b2", "Bryce: UPDATE своей строки\non_call = false", 720, 200, "q", 480, 100),
    N("res", "Обе транзакции делают COMMIT:\nна дежурстве 0 врачей", 300, 420, "r", 600, 100),
    N("fix", "Защита: serializable\nили SELECT ... FOR UPDATE\nна строки врачей смены", 300, 640, "g", 600, 110),
], edges=[E("a1", "a2"), E("b1", "b2"), E("a2", "res"), E("b2", "res"),
          E("res", "fix", "как избежать", dashed=True)])

# Section "Serializability": three ways to implement it (own diagram)
D["ch08-serializable-options"] = dict(items=[
    T("Три способа получить serializability", 0, -60, 24, "#1971c2"),
    N("s", "Serial execution\nодин поток,\nstored procedures\nVoltDB, Redis, Datomic", 0, 0, "pu", 440, 150),
    N("l", "Two-phase locking (2PL)\nпессимистично:\nчитатели и писатели\nждут друг друга", 520, 0, "q", 440, 150),
    N("o", "Serializable snapshot\nisolation (SSI)\nоптимистично: проверка\nпри commit", 1040, 0, "g", 440, 150),
    N("s2", "Нужно: короткие транзакции,\nданные в памяти, запись\nв пределах одного shard", 0, 260, "n", 440, 120),
    N("l2", "Цена: нестабильная latency,\nчастые deadlock,\nдолгие чтения блокируют запись", 520, 260, "r", 440, 120),
    N("o2", "Цена: много abort\nпри высокой contention", 1040, 260, "r", 440, 120),
    T("Где: VoltDB и Redis — serial; MySQL и SQL Server — 2PL;\n"
      "PostgreSQL, CockroachDB, FoundationDB — SSI.", 0, 430, 18),
], edges=[E("s", "s2", dashed=True), E("l", "l2", dashed=True), E("o", "o2", dashed=True)])

# Fig 8-13 / 8-14: two-phase commit and the two points of no return
D["ch08-two-phase-commit"] = dict(items=[
    T("Two-phase commit (2PC): атомарный commit на нескольких узлах", 0, -80, 24, "#1971c2"),
    N("c1", "Фаза 1: координатор\nшлёт prepare:\n«можете сделать commit?»", 0, 90, "p", 380, 120),
    N("d1", "База 1: пишет данные\nна диск, голосует «да»", 580, 0, "db", 360, 100),
    N("d2", "База 2: пишет данные\nна диск, голосует «да»", 580, 200, "db", 360, 100),
    N("cp", "Commit point: координатор\nзаписал решение\nв свой журнал", 1140, 90, "y", 380, 120),
    N("c2", "Фаза 2: commit всем,\nповторять, пока\nне получится", 1140, 430, "g", 380, 120),
    N("e1", "База 1: commit,\nснимает блокировки", 580, 360, "db", 360, 100),
    N("e2", "База 2: commit,\nснимает блокировки", 580, 560, "db", 360, 100),
    T("Две точки невозврата: участник ответил «да» — он уже не может отменить сам;\n"
      "координатор записал решение — оно окончательное. Если координатор упал между ними,\n"
      "участник остаётся in doubt и держит блокировки, пока координатор не вернётся.",
      0, 720, 18),
], edges=[E("c1", "d1", "prepare"), E("c1", "d2", "prepare"),
          E("d1", "cp", "да"), E("d2", "cp", "да"), E("cp", "c2"),
          E("c2", "e1", "commit"), E("c2", "e2", "commit")])

if __name__ == "__main__":
    run_all(D)
