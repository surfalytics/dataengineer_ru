#!/usr/bin/env python3
"""Chapter 9 (The Trouble with Distributed Systems) diagrams. Usage: ch09_diagrams.py [name ...]  (no args = all)
Reused without sources (1st-edition images): ch09-lost-request.png, ch09-clocks.png."""
from excb import N, E, Z, T, run_all

D = {}

# Fig 9-3: LWW with skewed clocks loses an increment
D["ch09-lww-clock-skew"] = dict(items=[
    T("LWW и часы с разницей меньше 3 мс", 0, -70, 26, "#1e1e1e"),
    N("a", "Клиент A пишет x = 1\nна узел 1.\nЧасы узла 1: 42,004 с", 0, 0, "p", 340, 120),
    N("b", "Узел 3 получает x = 1\n(репликация)", 460, 0, "n", 340, 120),
    N("c", "Клиент B: x = x + 1\nна узле 3, теперь x = 2.\nЧасы узла 3: 42,003 с", 920, 0, "p", 340, 120),
    N("d", "Узел 2 получает обе записи", 460, 260, "n", 340, 100),
    N("e", "LWW на узле 2:\n42,004 > 42,003,\nпобеждает x = 1", 460, 470, "r", 340, 120),
    N("f", "Инкремент потерян:\nx = 2 отброшен,\nошибки никто не видит", 920, 470, "r", 340, 120),
], edges=[E("a", "b"), E("b", "c", "потом"), E("a", "d", "x = 1, ts 42,004"), E("c", "d", "x = 2, ts 42,003"),
          E("d", "e"), E("e", "f")])

# Fig 9-4, 9-5, 9-6: zombie client and fencing token (redrawn under the old file name)
D["ch09-fencing-token"] = dict(items=[
    T("Fencing token защищает от «зомби»-клиента", 0, -70, 26, "#1e1e1e"),
    N("l1", "Lock service выдаёт lease\nклиенту 1: token 33", 0, 0, "p", 340, 100),
    N("p", "Клиент 1 на паузе GC.\nLease истёк", 460, 0, "r", 340, 100),
    N("l2", "Lock service выдаёт lease\nклиенту 2: token 34", 920, 0, "p", 340, 100),
    N("w2", "Клиент 2 пишет\nс token 34: принято", 920, 260, "g", 340, 100),
    N("z", "Клиент 1 просыпается\nи пишет с token 33", 460, 260, "q", 340, 100),
    N("s", "Хранилище: 33 < 34,\nзапись отклонена", 0, 260, "pu", 340, 100),
    T("Хранилище помнит самый большой token и само проверяет каждую запись.", 0, 420, 20),
], edges=[E("l1", "p"), E("p", "l2"), E("l2", "w2"), E("p", "z", "пауза\nкончилась"), E("w2", "z", "потом"),
          E("z", "s")])

# Fig 9-7: fencing token inside the LWW timestamp of a leaderless store
D["ch09-fencing-replicas"] = dict(items=[
    T("Fencing token в старших цифрах timestamp", 0, -70, 26, "#1e1e1e"),
    N("c2", "Клиент 2, token 34:\ntimestamp 34…", 0, 240, "p", 320, 110),
    N("r1", "Реплика 1:\nоставляет 34…", 560, 0, "db", 320, 110),
    N("r2", "Реплика 2:\nоставляет 34…", 560, 240, "db", 320, 110),
    N("r3", "Реплика 3\n(была недоступна):\nберёт 33…", 560, 480, "y", 320, 110),
    N("c1", "Зомби-клиент 1,\ntoken 33: timestamp 33…", 1120, 240, "r", 320, 110),
    N("q", "Кворумное чтение\nвыберет 34…, а read repair\nисправит реплику 3", 560, 720, "g", 320, 130),
], edges=[E("c2", "r1", "OK"), E("c2", "r2", "OK"), E("c2", "r3", "не дошла", dashed=True),
          E("c1", "r1", "игнор"), E("c1", "r2", "игнор"), E("c1", "r3", "OK"), E("r3", "q")])

if __name__ == "__main__":
    run_all(D)
