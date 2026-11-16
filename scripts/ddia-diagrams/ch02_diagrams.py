#!/usr/bin/env python3
"""Chapter 2 (Defining Nonfunctional Requirements) diagrams. Usage: ch02_diagrams.py [name ...]  (no args = all)
ch02-percentiles.png is reused from the 1st-edition page (no source)."""
from excb import N, E, Z, T, run_all

D = {}

# Fig 2-2: fan-out on write into materialized home timelines; celebrity posts merged on read
D["ch02-fanout"] = dict(items=[
    N("author", "Пользователь\nпубликует пост", 0, 120, "n", 250, 100),
    N("posts", "Таблица posts", 330, 120, "db", 250, 100),
    N("fan", "Fan-out: найти\nвсех подписчиков", 660, 120, "pu", 250, 100),
    N("t1", "Лента подписчика 1", 1000, 0, "db", 250, 90),
    N("t2", "Лента подписчика 2", 1000, 120, "db", 250, 90),
    N("t3", "Лента подписчика 200", 1000, 240, "db", 250, 90),
    N("read", "Подписчик открывает\nленту: готовый\nрезультат из кэша", 1330, 105, "g", 270, 130),
    N("celeb", "Пост знаменитости:\nмиллионы подписчиков", 0, 440, "r", 250, 100),
    N("cstore", "Посты знаменитостей\nхранятся отдельно", 660, 440, "db", 250, 100),
    N("merge", "Слияние при чтении:\nлента + посты\nзнаменитостей", 1330, 425, "g", 270, 130),
    N("sum", "Без материализации: 2 млн чтений ленты/с × 200 подписок = 400 млн выборок/с.\n"
             "С fan-out: 5 800 постов/с × 200 подписчиков = около 1,16 млн записей в ленты/с.", 0, 640, "y", 1600, 100),
], edges=[E("author", "posts"), E("posts", "fan"), E("fan", "t1"), E("fan", "t2"), E("fan", "t3"),
          E("t1", "read"), E("t2", "read"), E("t3", "read"),
          E("celeb", "cstore", "без fan-out"), E("cstore", "merge"), E("read", "merge", "при чтении")])

# Fig 2-4: response time = network latency + queueing delay + service time
D["ch02-response-time"] = dict(items=[
    Z("Сервер", 515, -80, 540, 230),
    N("c1", "Клиент\nотправляет запрос", 0, 0, "n", 220, 110),
    N("n1", "Сетевая\nзадержка", 270, 0, "y", 220, 110),
    N("q", "Ожидание\nв очереди\n(queueing delay)", 540, 0, "r", 220, 110),
    N("s", "Обработка\n(service time)", 810, 0, "p", 220, 110),
    N("n2", "Сетевая\nзадержка ответа", 1080, 0, "y", 220, 110),
    N("c2", "Клиент\nполучает ответ", 1350, 0, "g", 220, 110),
    N("rt", "Response time: всё время от отправки до ответа. Его видит клиент, поэтому мерить нужно на клиенте", 0, 220, "q", 1570, 80),
    N("lat", "Latency: время, когда запрос никто не обрабатывает (сеть и очереди)", 0, 330, "y", 1570, 80),
], edges=[E("c1", "n1"), E("n1", "q"), E("q", "s"), E("s", "n2"), E("n2", "c2")])

# redraw of the 1st-edition picture with 2nd-edition content: three kinds of faults and how to tolerate them
D["ch02-faults"] = dict(items=[
    N("hw", "Сбои железа\nдиски, RAM, CPU, ЦОД.\nПочти независимые", 0, 0, "q", 400, 120),
    N("sw", "Ошибки в ПО\nодин баг на всех узлах.\nСильно связаны", 470, 0, "r", 400, 120),
    N("hu", "Ошибки людей\nчаще всего: изменения\nконфигурации", 940, 0, "pu", 400, 120),
    N("hw2", "Redundancy: RAID,\nрезервное питание,\nузлы в разных зонах", 0, 200, "db", 400, 120),
    N("sw2", "Тесты, изоляция процессов,\ncrash и рестарт,\nмониторинг", 470, 200, "p", 400, 120),
    N("hu2", "Тесты, быстрый откат,\nпостепенный rollout,\nblameless postmortem", 940, 200, "p", 400, 120),
    N("ft", "Fault-tolerant система: fault одной части не становится failure всей системы", 0, 400, "g", 1340, 90),
], edges=[E("hw", "hw2"), E("sw", "sw2"), E("hu", "hu2"), E("hw2", "ft"), E("sw2", "ft"), E("hu2", "ft")])

if __name__ == "__main__":
    run_all(D)
