"""Глава 9: static, dynamic и continuous batching на одном потоке запросов.
Время идёт шагами decode: за один шаг каждый запрос в batch получает один токен (шаг = 10 мс).
Запрос с длиной 40 нужен 40 шагов. Prefill для простоты не считаем.
Правила:
  static     старт, когда набралось B запросов; все получают ответ, когда закончился самый длинный
  dynamic    старт, когда набралось B запросов ИЛИ самый старый ждёт уже W шагов; ответ тоже общий
  continuous готовый запрос уходит сразу, на его место на следующем шаге встаёт ожидающий
Запуск: python3 scripts/ai-engineering-code/ch09_batching_sim.py   (только стандартная библиотека)"""
import random

STEP_MS = 10
B = 8            # максимум запросов в batch
W = 10           # окно dynamic batching: 10 шагов = 100 мс


def make_requests(n, seed, gap):
    rng = random.Random(seed)
    t, reqs = 0.0, []
    for _ in range(n):
        t += rng.expovariate(1 / gap)                                  # в среднем один запрос раз в gap шагов
        length = rng.randint(5, 20) if rng.random() < 0.7 else rng.randint(60, 150)   # 70% коротких ответов
        reqs.append({"arrive": int(t), "length": length})
    return reqs


def run_batched(reqs, window):
    """static (window=None) и dynamic (window=W): batch выполняется целиком, ответ общий."""
    queue, done, t, i, busy_steps, useful = [], [], 0, 0, 0, 0
    pending = sorted(reqs, key=lambda r: r["arrive"])
    while i < len(pending) or queue:
        while i < len(pending) and pending[i]["arrive"] <= t:
            queue.append(pending[i]); i += 1
        no_more = i >= len(pending)
        ready = len(queue) >= B or no_more or (window is not None and queue and t - queue[0]["arrive"] >= window)
        if not queue or not ready:
            t += 1
            continue
        batch, queue = queue[:B], queue[B:]
        run = max(r["length"] for r in batch)
        t += run
        busy_steps += run
        useful += sum(r["length"] for r in batch)
        for r in batch:
            done.append((r, t))
    return done, busy_steps * B, useful


def run_continuous(reqs):
    pending = sorted(reqs, key=lambda r: r["arrive"])
    queue, active, done, t, i, busy_steps, useful = [], [], [], 0, 0, 0, 0
    while i < len(pending) or queue or active:
        while i < len(pending) and pending[i]["arrive"] <= t:
            queue.append(pending[i]); i += 1
        while queue and len(active) < B:
            req = queue.pop(0)
            active.append([req, req["length"]])               # [запрос, сколько токенов осталось]
        if active:
            busy_steps += 1
            useful += len(active)
            for a in active:
                a[1] -= 1
            t += 1
            for a in [a for a in active if a[1] == 0]:
                done.append((a[0], t))
                active.remove(a)
        else:
            t += 1
    return done, busy_steps * B, useful


def pct(xs, p):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(round((len(xs) - 1) * p / 100)))]


def report(title, gap):
    reqs = make_requests(120, seed=3, gap=gap)
    n_short = sum(r["length"] <= 20 for r in reqs)
    print(f"{title}: запрос раз в {gap} шагов ({gap * STEP_MS} мс), всего {len(reqs)}, коротких (до 20 токенов) {n_short}")
    print(f"{'метод':<12}{'средняя, с':>11}{'p95, с':>8}{'короткие, с':>13}{'всё готово, с':>15}{'слоты заняты':>14}")
    for name, (done, slots, useful) in [
        ("static", run_batched(reqs, None)),
        ("dynamic", run_batched(reqs, W)),
        ("continuous", run_continuous(reqs)),
    ]:
        lat = [(fin - r["arrive"]) * STEP_MS / 1000 for r, fin in done]
        lat_short = [(fin - r["arrive"]) * STEP_MS / 1000 for r, fin in done if r["length"] <= 20]
        makespan = max(fin for _, fin in done) * STEP_MS / 1000
        print(f"{name:<12}{sum(lat) / len(lat):>11.1f}{pct(lat, 95):>8.1f}{sum(lat_short) / len(lat_short):>13.1f}"
              f"{makespan:>15.1f}{useful / slots:>14.0%}")
    print()


print(f"batch до {B} запросов, окно dynamic = {W * STEP_MS} мс. Колонки: 'короткие' = средняя latency ответов до 20 токенов,")
print("'всё готово' = когда закончился последний запрос, 'слоты заняты' = доля слотов batch с полезной работой\n")
report("Лёгкая нагрузка", gap=20)
report("Тяжёлая нагрузка", gap=8)
