#!/usr/bin/env python3
"""DDIA 2nd ed., chapter 10 (Consistency and Consensus) diagrams. Usage: ch10_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

# main (own): eventual consistency -> weaker models -> linearizability (redrawn for the 2nd edition)
D["ch10-consistency-levels"] = dict(items=[
    N("ev", "Eventual consistency\nРеплики сойдутся,\nно неизвестно когда", 0, 0, "r", 340, 120),
    N("mid", "Слабые модели\nread-after-write,\nmonotonic reads,\nconsistent prefix", 470, 0, "y", 340, 120),
    N("lin", "Linearizability\nКак одна копия данных,\nоперации атомарны", 940, 0, "g", 340, 120),
    N("ev2", "Конфликты и устаревшие\nчтения видит\nприложение", 0, 220, "n", 340, 120),
    N("mid2", "Частичные гарантии\nпри лаге репликации\n(глава 6)", 470, 220, "n", 340, 120),
    N("lin2", "Самая сильная модель.\nМедленнее, при разрыве\nсети часть узлов недоступна", 940, 220, "n", 340, 120),
    T("Сильнее гарантия: проще писать приложение, но выше задержка и ниже доступность при сбоях сети.", 0, 390, 20, "#495057"),
], edges=[E("ev", "mid"), E("mid", "lin"), E("ev", "ev2"), E("mid", "mid2"), E("lin", "lin2")])

# Figure 10-5: two channels (file storage and queue) -> race condition
D["ch10-cross-channel"] = dict(items=[
    N("web", "Веб-сервер", 0, 0, "p", 280, 100),
    N("store", "Хранилище файлов\n(реплики догоняют\nлидера)", 760, 0, "db", 300, 110),
    N("queue", "Очередь сообщений", 0, 300, "q", 280, 100),
    N("tr", "Транскодер видео", 760, 300, "pu", 300, 100),
    T("Если хранилище не linearizable, сообщение в очереди может обогнать репликацию.\nТогда на шаге 4 транскодер увидит старый файл или ничего.", 0, 460, 20, "#495057"),
], edges=[E("web", "store", "1. записать видео"), E("web", "queue", "2. задача"),
          E("queue", "tr", "3. доставить задачу"), E("tr", "store", "4. прочитать видео")])

# Figure 10-9: Lamport timestamps in a chat
D["ch10-lamport-clock"] = dict(items=[
    N("a", "Алия пишет вопрос\nметка (1, Алия)", 0, 0, "p", 300, 100),
    N("c", "Калеб пишет сообщение\nметка (1, Калеб)", 0, 280, "y", 300, 100),
    N("b", "Брайс получает оба:\nсвой счётчик 0 → 1", 560, 140, "n", 300, 100),
    N("r", "Брайс отвечает Алие\nметка (2, Брайс)", 1120, 140, "g", 300, 100),
    T("Порядок: (1, Алия) < (1, Калеб) < (2, Брайс).\nСначала сравниваем счётчик, при равенстве ID узла.", 0, 440, 20, "#495057"),
], edges=[E("a", "b"), E("c", "b"), E("b", "r", "счётчик + 1")])

# own, redrawn from the 1st-edition picture: all these problems reduce to consensus
D["ch10-consensus-equivalence"] = dict(items=[
    N("cas", "Linearizable CAS", 0, 0, "p", 300, 100),
    N("log", "Shared log\n(total order broadcast)", 450, 0, "p", 300, 100),
    N("ac", "Atomic commit\n(commit или abort везде)", 900, 0, "p", 300, 100),
    N("cons", "Консенсус:\nузлы выбирают одно значение\nи не меняют решение", 400, 250, "g", 400, 120),
    N("lock", "Блокировки и lease,\nвыбор leader", 0, 520, "pu", 300, 100),
    N("faa", "Fetch-and-add\n(генератор ID)", 450, 520, "y", 300, 100),
    N("uniq", "Ограничения\nуникальности", 900, 520, "pu", 300, 100),
    T("Решили одну задачу отказоустойчиво: можно построить и остальные.\nFetch-and-add решает консенсус только для двух узлов.", 0, 680, 20, "#495057"),
], edges=[E("cons", "cas"), E("cons", "log"), E("cons", "ac"), E("cons", "lock"),
          E("cons", "faa", "только 2 узла", dashed=True), E("cons", "uniq")])

# own, redrawn: 2PC vs voting in consensus (2PC itself is explained in chapter 8)
D["ch10-two-phase-commit"] = dict(items=[
    Z("2PC: решает координатор", -30, -70, 680, 580),
    N("co", "Координатор", 170, 0, "q", 260, 100),
    N("p1", "Участник 1", 0, 300, "n", 180, 90),
    N("p2", "Участник 2", 210, 300, "n", 180, 90),
    N("p3", "Участник 3", 420, 300, "n", 180, 90),
    T("Нужен yes от всех участников.\nКоординатор упал: все ждут.", 0, 430, 20, "#e03131"),
    Z("Консенсус: решает кворум", 700, -70, 820, 580),
    N("ld", "Leader, эпоха 7", 960, 0, "g", 280, 100),
    N("n1", "Узел", 730, 300, "g", 130, 90),
    N("n2", "Узел", 885, 300, "g", 130, 90),
    N("n3", "Узел", 1040, 300, "g", 130, 90),
    N("n4", "Узел", 1195, 300, "n", 130, 90),
    N("n5", "Узел", 1350, 300, "n", 130, 90),
    T("Хватает 3 из 5. Leader упал: любой узел\nначинает выборы с эпохой 8.", 730, 430, 20, "#2f9e44"),
], edges=[E("co", "p1"), E("co", "p2", "prepare?"), E("co", "p3"),
          E("ld", "n1"), E("ld", "n2"), E("ld", "n3", "голосуем?"), E("ld", "n4"), E("ld", "n5")])

if __name__ == "__main__":
    run_all(D)
