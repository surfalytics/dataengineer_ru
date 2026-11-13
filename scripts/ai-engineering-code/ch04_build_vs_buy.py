"""Глава 4: API или self-hosting. Считаем деньги и память GPU.
1) Стоимость API растёт вместе с объёмом, стоимость своего кластера почти фиксирована. Ищем точку безубыточности.
2) Какой размер модели помещается в GPU на 16, 24, 48 и 80 ГБ (только веса). Отсюда популярные размеры 7B и 65B.
Все цены выдуманы для примера. Подставьте свои. Электричество и простои в расчёте не учтены.
Запуск: python3 scripts/ai-engineering-code/ch04_build_vs_buy.py   (только стандартная библиотека)"""

# ---------- 1. деньги ----------
API_PRICE_PER_1M = 5.0          # $ за 1 млн токенов (вход и выход вместе, усреднено)
GPU_HOUR = 2.5                  # $ за час одной GPU
GPUS = 8
CLUSTER_PER_MONTH = GPUS * GPU_HOUR * 24 * 30
ENGINEERS_PER_MONTH = 1.5 * 15000   # 1,5 инженера на оптимизацию, хостинг и поддержку
CAPACITY_PER_DAY = 1_000_000_000    # кластер тянет не больше 1 млрд токенов в день
DAYS = 30

print(f"кластер: {GPUS} GPU x ${GPU_HOUR}/ч = ${CLUSTER_PER_MONTH:,.0f} в месяц; инженеры: ${ENGINEERS_PER_MONTH:,.0f} в месяц")
print("\n== 1. Стоимость в месяц при разном объёме")
print(f"{'токенов в день':>15} {'API, $':>10} {'self-host, $':>13} {'self-host, $ за 1M токенов':>28}")
for tokens_per_day in [1e6, 1e7, 1e8, 5e8, 1e9]:
    api = tokens_per_day * DAYS * API_PRICE_PER_1M / 1e6
    own = CLUSTER_PER_MONTH + ENGINEERS_PER_MONTH
    own_per_1m = own / (tokens_per_day * DAYS / 1e6)
    print(f"{tokens_per_day:15,.0f} {api:10,.0f} {own:13,.0f} {own_per_1m:28.2f}")

fixed = CLUSTER_PER_MONTH + ENGINEERS_PER_MONTH
break_even = fixed / (DAYS * API_PRICE_PER_1M / 1e6)
print(f"\nточка безубыточности: {break_even:,.0f} токенов в день ({break_even / CAPACITY_PER_DAY:.0%} мощности кластера)")
print(f"без своих инженеров (платим только GPU): {CLUSTER_PER_MONTH / (DAYS * API_PRICE_PER_1M / 1e6):,.0f} токенов в день")
print("Цена API за 1M токенов не меняется. Цена своего кластера за 1M токенов падает, пока кластер не заполнен.")

# ---------- 2. память GPU ----------
GPU_GB = [16, 24, 48, 80]
BYTES = {"fp16": 2.0, "int8": 1.0, "int4": 0.5}

print("\n== 2. Какая GPU вмещает веса модели (без KV cache и запаса на активации)")
print(f"{'модель':>8} {'формат':>6} {'веса, ГБ':>9}  минимальная GPU")
for params_b in [7, 13, 34, 65]:
    for fmt, b in BYTES.items():
        gb = params_b * b      # млрд параметров x байт на параметр = ГБ
        fit = next((g for g in GPU_GB if gb <= g), None)
        print(f"{params_b:>7}B {fmt:>6} {gb:9.1f}  {fit and f'{fit} ГБ' or 'не влезает в одну GPU'}")
print("7B в fp16 (14 ГБ) почти заполняет GPU на 16 ГБ. 65B в int8 (65 ГБ) помещается в 80 ГБ. Поэтому такие размеры так популярны.")
