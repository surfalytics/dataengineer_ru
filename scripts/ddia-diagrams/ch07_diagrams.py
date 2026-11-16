#!/usr/bin/env python3
"""Chapter 7 (Sharding) diagrams. Usage: ch07_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

# main + fig 7-2, 7-5: key-range vs hash-range sharding
D["ch07-partitioning-schemes"] = dict(items=[
    Z("Sharding по диапазону ключей", -20, -70, 560, 560),
    Z("Sharding по диапазону хешей", 620, -70, 560, 560),
    N("kr", "Ключи отсортированы.\nshard 0: A–F, shard 1: G–P,\nshard 2: Q–Z", 0, 0, "p", 520, 110),
    N("krp", "Плюс: range-запрос\nчитает один shard", 0, 190, "g", 520, 90),
    N("krm", "Риск: hot spot, если ключ — время.\nРешение: впереди ставят sensor ID", 0, 360, "r", 520, 100),
    N("hr", "hash(key) от 0 до 65 535.\nshard 0: 0–16 383,\nshard 1: 16 384–32 767, ...", 640, 0, "db", 520, 110),
    N("hrp", "Плюс: даже соседние ключи\nрасходятся по разным shard", 640, 190, "g", 520, 90),
    N("hrm", "Минус: range-запрос по ключу\nидёт во все shard", 640, 360, "r", 520, 100),
    N("ck", "Составной ключ: первая колонка — partition key,\nостальные колонки задают порядок внутри shard.\n"
            "Range-запрос внутри одного partition key остаётся быстрым", 0, 580, "y", 1160, 120),
], edges=[E("kr", "krp"), E("krp", "krm"), E("hr", "hrp"), E("hrp", "hrm"),
          E("krm", "ck", dashed=True), E("hrm", "ck", dashed=True)])

# fig 7-3 + 7-4: hash mod N vs fixed number of shards
D["ch07-fixed-shards"] = dict(items=[
    Z("hash mod N", -20, -70, 560, 600),
    Z("Фиксированное число shard", 620, -70, 560, 600),
    N("m3", "3 узла:\nузел = hash(key) % 3", 0, 0, "p", 520, 100),
    N("m4", "4 узла:\nузел = hash(key) % 4", 0, 200, "p", 520, 100),
    N("mr", "Почти у всех ключей меняется узел:\nв примере переехало 75% ключей", 0, 400, "r", 520, 100),
    N("f1", "12 shard, по 4 на каждый из 3 узлов.\nshard = hash(key) % 12", 640, 0, "p", 520, 100),
    N("f2", "Новый узел забирает\nпо одному shard у каждого узла", 640, 200, "p", 520, 100),
    N("fr", "Ключ остаётся в своём shard.\nМеняется только то,\nна каком узле лежит shard:\nпереехало 25% ключей", 640, 400, "g", 520, 130),
    N("nt", "Число shard выбирают заранее. Мало shard — нужен дорогой resharding.\n"
            "Слишком крупные shard — дорогие rebalancing и восстановление", 0, 600, "y", 1160, 100),
], edges=[E("m3", "m4", "добавили узел"), E("m4", "mr"), E("f1", "f2", "добавили узел"), E("f2", "fr")])

# fig 7-7 + 7-8: three ways of request routing, coordination service
D["ch07-rebalancing-routing"] = dict(items=[
    T("1. Через любой узел", 0, -60, 22, "#1971c2"),
    T("3. Клиент знает карту", 380, -60, 22, "#1971c2"),
    T("2. Через routing tier", 760, -60, 22, "#1971c2"),
    N("c1", "Клиент", 0, 0, "n", 300, 90),
    N("c3", "Клиент\nсо своей картой shard", 380, 0, "n", 300, 90),
    N("c2", "Клиент", 760, 0, "n", 300, 90),
    N("any", "Любой узел\n(round-robin\nload balancer)", 0, 220, "p", 300, 110),
    N("rt", "Routing tier:\nload balancer,\nкоторый знает shard", 760, 220, "pu", 300, 110),
    N("o1", "Узел —\nвладелец shard", 0, 460, "db", 300, 100),
    N("o3", "Узел —\nвладелец shard", 380, 460, "db", 300, 100),
    N("o2", "Узел —\nвладелец shard", 760, 460, "db", 300, 100),
    N("co", "Сервис координации\n(ZooKeeper, etcd):\nкакой shard на каком узле", 1280, 220, "y", 300, 110),
    T("При rebalancing shard переезжают на другие узлы. Все, кто направляет запросы, должны сразу узнать об этом",
      0, 620, 20, "#495057"),
], edges=[E("c1", "any"), E("any", "o1", "пересылает"), E("c3", "o3", "напрямую"),
          E("c2", "rt"), E("rt", "o2"), E("co", "rt", "уведомляет", dashed=True),
          E("o2", "co", "узел\nрегистрируется", dashed=True)])

# fig 7-9 + 7-10: local vs global secondary index
D["ch07-secondary-indexes"] = dict(items=[
    Z("Local secondary index", -20, -70, 560, 600),
    Z("Global secondary index", 620, -70, 560, 600),
    N("l1", "Каждый shard индексирует\nтолько свои записи:\nв shard 0: color:red = [191, 306],\n"
            "в shard 1: color:red = [768]", 0, 0, "p", 520, 130),
    N("l2", "Запись: обновляется один shard", 0, 220, "g", 520, 90),
    N("l3", "Поиск по цвету: запрос во все shard\nи склейка ответов. Растёт tail latency", 0, 390, "r", 520, 100),
    N("g1", "Индекс разбит по значению (term):\nцвета a–r в shard индекса 0,\nцвета s–z в shard индекса 1",
      640, 0, "db", 520, 130),
    N("g2", "Запись: может задеть несколько\nshard индекса, часто асинхронно", 640, 220, "r", 520, 90),
    N("g3", "Поиск color = red: один shard индекса.\nНо сами записи лежат в разных shard", 640, 390, "g", 520, 100),
    N("nt", "Local: MongoDB, Cassandra, Elasticsearch. Global: CockroachDB, TiDB, YugabyteDB.\nDynamoDB умеет оба",
      0, 570, "n", 1160, 90),
], edges=[E("l1", "l2"), E("l2", "l3"), E("g1", "g2"), E("g2", "g3")])

if __name__ == "__main__":
    run_all(D)
