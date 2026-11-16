#!/usr/bin/env python3
"""Chapter 12 (Stream Processing) diagrams. Usage: ch12_diagrams.py [name ...]  (no args = all)
ch12-cdc-vs-dual-writes.png and ch12-time-windows.png are reused from the 1st-edition page (no source)."""
from excb import N, E, Z, T, run_all

D = {}

# Fig 12-1 + 12-3: two kinds of message broker (redrawn: shard instead of partition)
D["ch12-brokers"] = dict(items=[
    Z("AMQP/JMS: сообщение уходит одному consumer и удаляется после ack", -30, -80, 1560, 330),
    N("p1", "Producers", 0, 50, "n", 240, 100),
    N("q", "Очередь брокера:\nm1, m2, m3, m4", 340, 50, "q", 300, 100),
    N("c1", "Consumer 1", 800, -10, "p", 240, 90),
    N("c2", "Consumer 2", 800, 120, "p", 240, 90),
    T("После ack сообщение\nудалено: перечитать\nнельзя", 1120, 40, 20, "#e8590c"),
    Z("Log-based: topic = набор shard, у каждого сообщения свой offset", -30, 290, 1560, 540),
    N("p2", "Producers:\nключ → shard", 0, 530, "n", 240, 100),
    N("s0", "Shard 0:  0 1 2 3 4 5", 340, 410, "db", 300, 80),
    N("s1", "Shard 1:  0 1 2 3", 340, 540, "db", 300, 80),
    N("s2", "Shard 2:  0 1 2 3 4", 340, 670, "db", 300, 80),
    N("a1", "Группа A, consumer 1\nчитает shard 0 и 1", 780, 360, "p", 300, 90),
    N("a2", "Группа A, consumer 2\nчитает shard 2", 780, 720, "p", 300, 90),
    N("b1", "Группа B, consumer 1\nчитает все shard", 1200, 540, "g", 300, 90),
    T("Чтение не удаляет сообщение.\nКаждая группа хранит\nсвой offset", 1170, 370, 20, "#0c8599"),
], edges=[E("p1", "q"), E("q", "c1", "m1, m3"), E("q", "c2", "m2, m4"),
          E("p2", "s0"), E("p2", "s1"), E("p2", "s2"),
          E("s0", "a1"), E("s1", "a1"), E("s2", "a2"),
          E("s0", "b1"), E("s1", "b1"), E("s2", "b1")])

# Fig 12-6: log compaction (our own data: product prices, same as the DuckDB practice)
_top = [("milk = 80", "p"), ("tea = 50", "g"), ("milk = 85", "p"), ("coffee = 120", "y"),
        ("tea = 55", "g"), ("milk = 90", "p"), ("coffee = null\n(tombstone)", "r"), ("tea = 60", "g")]
_items = [T("Лог до compaction: 8 записей (offset сверху)", 0, -50, 22, "#495057")]
for i, (txt, k) in enumerate(_top):
    _items.append(N(f"t{i}", f"{i}\n{txt}", i * 175, 0, k, 160, 90))
_items += [
    T("После compaction: по одной последней записи на ключ.\nTombstone удаляет ключ coffee целиком.", 0, 190, 22, "#495057"),
    N("b5", "5\nmilk = 90", 5 * 175, 260, "p", 160, 90),
    N("b7", "7\ntea = 60", 7 * 175, 260, "g", 160, 90),
]
D["ch12-log-compaction"] = dict(items=_items, edges=[E("t5", "b5"), E("t7", "b7")])

if __name__ == "__main__":
    run_all(D)
