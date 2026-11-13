"""Глава 6: поиск ближайших соседей: точный перебор (k-NN) против приближённого (ANN).
Мы пишем два простых ANN-алгоритма с нуля: IVF (кластеры k-means) и LSH (случайные гиперплоскости)
и меряем две вещи: recall (какую долю настоящих соседей нашли) и число проверенных vectors
(это замена скорости: чем меньше проверок, тем быстрее). Данные — случайные кластеры с фиксированным seed.
Запуск: python3 -I scripts/ai-engineering-code/ch06_ann_search.py   (только стандартная библиотека)"""
import math
import random

rng = random.Random(7)
DIM, N_CLUSTERS, PER_CLUSTER, K = 16, 20, 100, 5

print("== 0. Данные")
centers = [[rng.uniform(-10, 10) for _ in range(DIM)] for _ in range(N_CLUSTERS)]
data = [[c + rng.gauss(0, 4.0) for c in center] for center in centers for _ in range(PER_CLUSTER)]
queries = [[c + rng.gauss(0, 4.0) for c in rng.choice(centers)] for _ in range(60)]
print(f"vectors в базе: {len(data)}, размерность: {DIM}, запросов: {len(queries)}, ищем k = {K}")


def top_k(q, candidate_ids, k=K):
    return sorted(candidate_ids, key=lambda i: math.dist(q, data[i]))[:k]


print("\n== 1. Точный перебор (k-NN): проверяет каждый vector")
truth = [set(top_k(q, range(len(data)))) for q in queries]
print(f"проверено vectors на запрос: {len(data)} (все); recall = 1.00 по определению")

print("\n== 2. IVF: делим vectors на кластеры k-means, при запросе смотрим только ближайшие кластеры")


def kmeans(points, k, iters=8):
    cents = [points[i][:] for i in rng.sample(range(len(points)), k)]
    for _ in range(iters):
        groups = [[] for _ in range(k)]
        for p in points:
            groups[min(range(k), key=lambda j: math.dist(p, cents[j]))].append(p)
        for j, g in enumerate(groups):
            if g:
                cents[j] = [sum(x) / len(g) for x in zip(*g)]
    return cents


cents = kmeans(data, N_CLUSTERS)
cells = [[] for _ in range(N_CLUSTERS)]
for i, p in enumerate(data):
    cells[min(range(N_CLUSTERS), key=lambda j: math.dist(p, cents[j]))].append(i)
print(f"кластеров: {N_CLUSTERS}, размеры от {min(map(len, cells))} до {max(map(len, cells))}")
build_ivf = (8 + 1) * len(data) * N_CLUSTERS  # 8 итераций k-means + финальное распределение: расстояний до центров
print(f"построение индекса: около {build_ivf} вычислений расстояния")
print(f"{'nprobe':>7} {'recall':>8} {'проверено vectors':>18}")
for nprobe in (1, 2, 4, 8):
    hit, checked = 0, 0
    for q, t in zip(queries, truth):
        near = sorted(range(N_CLUSTERS), key=lambda j: math.dist(q, cents[j]))[:nprobe]
        cand = [i for j in near for i in cells[j]]
        hit += len(set(top_k(q, cand)) & t)
        checked += len(cand) + N_CLUSTERS  # плюс сравнение с центрами кластеров
    print(f"{nprobe:>7} {hit / (K * len(queries)):>8.2f} {checked / len(queries):>18.0f}")
print("Больше кластеров на запрос -> выше recall, но больше проверок. Это и есть компромисс ANN.")

print("\n== 3. LSH: хэш по знакам проекций на случайные гиперплоскости, похожие vectors попадают в одну корзину")


def lsh_index(n_planes, seed):
    r = random.Random(seed)
    planes = [[r.gauss(0, 1) for _ in range(DIM)] for _ in range(n_planes)]

    def sig(p):
        return tuple(sum(a * b for a, b in zip(pl, p)) > 0 for pl in planes)

    buckets = {}
    for i, p in enumerate(data):
        buckets.setdefault(sig(p), []).append(i)
    return sig, buckets


print(f"{'planes':>7} {'tables':>7} {'построение':>11} {'recall':>8} {'проверено vectors':>18}")
for n_planes, n_tables in ((10, 1), (6, 1), (6, 4), (6, 8)):
    tables = [lsh_index(n_planes, 100 + t) for t in range(n_tables)]
    hit, checked = 0, 0
    for q, t in zip(queries, truth):
        cand = set()
        for sig, buckets in tables:
            cand.update(buckets.get(sig(q), []))
        hit += len(set(top_k(q, cand)) & t)
        checked += len(cand)
    build = len(data) * n_planes * n_tables  # проекций на плоскости при построении
    print(f"{n_planes:>7} {n_tables:>7} {build:>11} {hit / (K * len(queries)):>8.2f} {checked / len(queries):>18.0f}")
print("Меньше гиперплоскостей и больше таблиц -> выше recall, но больше проверок.")
print("На этих данных IVF достигает высокого recall за меньшее число проверок, чем LSH, но строить его дороже (k-means).")
print("Это компромисс «индекс против запроса»: подробный индекс строится дольше, зато запросы быстрее и точнее.")
