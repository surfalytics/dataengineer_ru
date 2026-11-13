"""Глава 9: метрики inference: TTFT, TPOT, перцентили, throughput и goodput.
Данные здесь придуманы: маленький журнал запросов и большой журнал из генератора с фиксированным seed.
В настоящем сервисе вы берёте такие же поля (время отправки, время первого токена, время конца, число токенов) из логов.
Формула из книги: общая latency = TTFT + TPOT * (число выходных токенов).
Запуск: python3 scripts/ai-engineering-code/ch09_latency_metrics.py   (только стандартная библиотека)"""
import random


def percentile(values, p):
    """Перцентиль с линейной интерполяцией (так же считает quantile_cont в DuckDB)."""
    xs = sorted(values)
    pos = (len(xs) - 1) * p / 100
    lo = int(pos)
    hi = min(lo + 1, len(xs) - 1)
    return xs[lo] + (xs[hi] - xs[lo]) * (pos - lo)


print("== 1. Среднее обманывает: 10 значений TTFT, одно из них выброс (3000 мс)")
ttft = [100, 102, 100, 100, 99, 104, 110, 90, 3000, 95]
print(f"среднее: {sum(ttft) / len(ttft):.0f} мс")
for p in (50, 90, 95, 99):
    print(f"p{p}: {percentile(ttft, p):.0f} мс")
print("Медиана (p50) показывает типичный запрос. Выброс виден в p90 и выше, его надо разобрать отдельно.")

print("\n== 2. Один запрос: общая latency = TTFT + TPOT * число токенов")
n_out, ttft_ms, tpot_ms = 1000, 200, 100
print(f"TTFT {ttft_ms} мс, TPOT {tpot_ms} мс, {n_out} токенов -> {(ttft_ms + tpot_ms * n_out) / 1000:.1f} с")
print(f"Скорость чтения: TPOT 120 мс = {1000 / 120:.1f} токена в секунду, этого хватает быстрому читателю")

print("\n== 3. Goodput: 10 запросов, SLO: TTFT <= 200 мс и TPOT <= 100 мс")
SLO_TTFT, SLO_TPOT = 200, 100
requests = [  # (TTFT мс, TPOT мс): те же 10 запросов, что на нашей схеме
    (150, 70), (180, 120), (220, 110), (250, 130), (140, 60),
    (260, 80), (170, 95), (210, 140), (190, 105), (230, 150),
]
ok = [(a, b) for a, b in requests if a <= SLO_TTFT and b <= SLO_TPOT]
window_s = 60  # пусть все 10 запросов закончились за 60 секунд
print(f"завершено запросов: {len(requests)} за {window_s} с -> throughput {len(requests) * 60 / window_s:.0f} RPM (запросов в минуту)")
print(f"уложились в оба SLO: {len(ok)} -> goodput {len(ok) * 60 / window_s:.0f} RPM")
only_ttft = sum(a <= SLO_TTFT for a, _ in requests)
only_tpot = sum(b <= SLO_TPOT for _, b in requests)
print(f"только по TTFT уложились {only_ttft}, только по TPOT {only_tpot}: нужны оба условия сразу")
print("Пример книги: 100 RPM, из них 30 в SLO -> goodput 30 RPM")

print("\n== 4. Большой журнал: 2000 запросов, генератор с seed")
rng = random.Random(11)
log = []
for _ in range(2000):
    in_tokens = int(rng.lognormvariate(6.0, 0.9))              # длина prompt: чаще 200-600, редко очень длинная
    out_tokens = max(5, int(rng.lognormvariate(5.0, 0.7)))     # длина ответа
    t_first = 60 + 0.25 * in_tokens + rng.gauss(0, 15)          # prefill растёт с длиной входа
    if rng.random() < 0.01:
        t_first += 1500                                         # редкий сетевой сбой
    t_next = max(20, rng.gauss(70, 18))                         # decode: время на токен
    log.append((in_tokens, out_tokens, max(t_first, 20), t_next))

first = [r[2] for r in log]
nxt = [r[3] for r in log]
print(f"{'метрика':<8}{'TTFT, мс':>10}{'TPOT, мс':>10}")
print(f"{'среднее':<8}{sum(first) / len(first):>10.0f}{sum(nxt) / len(nxt):>10.0f}")
for p in (50, 90, 95, 99):
    print(f"{'p' + str(p):<8}{percentile(first, p):>10.0f}{percentile(nxt, p):>10.0f}")

good = sum(1 for _, _, a, b in log if a <= SLO_TTFT and b <= SLO_TPOT)
print(f"\nв SLO (TTFT <= {SLO_TTFT}, TPOT <= {SLO_TPOT}): {good} из {len(log)} = {good / len(log):.1%}")

print("\nTTFT по длине входа (книга советует смотреть TTFT вместе с длиной входа):")
print(f"{'вход, токенов':<16}{'запросов':>9}{'медиана TTFT, мс':>18}")
for lo, hi in [(0, 250), (250, 500), (500, 1000), (1000, 100000)]:
    part = [a for i, _, a, _ in log if lo <= i < hi]
    label = f"{lo}-{hi}" if hi < 100000 else f"{lo}+"
    print(f"{label:<16}{len(part):>9}{percentile(part, 50):>18.0f}")

print("\n== 5. TTFT глазами пользователя: агент сначала думает скрыто")
steps = [("план (скрыт)", 1.2), ("вызов инструментов (скрыт)", 3.0)]
model_ttft = 0.2
hidden = sum(t for _, t in steps)
print(f"для модели первый токен приходит через {model_ttft:.1f} с")
print(f"пользователь видит первый токен через {model_ttft + hidden + model_ttft:.1f} с: скрытые шаги {hidden:.1f} с плюс первый токен ответа")
