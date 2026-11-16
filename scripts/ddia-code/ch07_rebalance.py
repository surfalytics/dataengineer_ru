# Глава 7: сколько ключей переезжает, когда в кластер из 3 узлов добавляют 4-й.
import hashlib

def h(key):  # стабильный хеш: одинаковый в любом процессе (в отличие от hash() в Python)
    return int(hashlib.md5(key.encode()).hexdigest(), 16)

keys = [f"user:{i}" for i in range(10_000)]

# 1. hash mod N: номер узла = хеш по модулю числа узлов
moved = sum(h(k) % 3 != h(k) % 4 for k in keys)
print(f"hash mod N:          переехало {moved / len(keys):.0%} ключей")

# 2. Фиксированное число shard: ключ -> shard не меняется, новый узел забирает целые shard
SHARDS = 12
old = {s: s % 3 for s in range(SHARDS)}             # по 4 shard на узел
new = dict(old)
for s in (0, 1, 2):                                 # узлы 0, 1, 2 отдают по одному shard узлу 3
    new[s] = 3
moved = sum(old[h(k) % SHARDS] != new[h(k) % SHARDS] for k in keys)
print(f"фиксированные shard: переехало {moved / len(keys):.0%} ключей")
