"""Глава 6: как оценивать агента: накопление ошибок, planning dataset, метрики сбоев планирования,
ablation tools, переходы между tools, эффективность и intent classifier с классом IRRELEVANT.
Планировщик здесь — mock, он нарочно ошибается с заданными вероятностями (seed фиксирован).
Настоящая часть — код оценки: он классифицирует каждый вызов и считает метрики, как вы считали бы по логам реального агента.
Запуск: python3 -I scripts/ai-engineering-code/ch06_agent_eval.py   (только стандартная библиотека)"""
import random
from collections import Counter, defaultdict

print("== 1. Ошибки накапливаются: точность на шаг -> успех всей задачи")
print(f"{'на шаг':>7} {'5 шагов':>9} {'10 шагов':>9} {'20 шагов':>9} {'100 шагов':>10}")
for p in (0.90, 0.95, 0.99):
    print(f"{p:>7.2f} " + " ".join(f"{p ** n:>{w}.1%}" for n, w in ((5, 9), (10, 9), (20, 9), (100, 10))))
print("При 95% на шаг 10 шагов дают около 60%, а 100 шагов — около 0,6%.")

# ---------------------------------------------------------------- planning dataset
INVENTORY = {  # tool inventory: имя -> список параметров
    "get_today_date": [],
    "fetch_top_products": ["start_date", "end_date", "num_products"],
    "fetch_product_info": ["product_name"],
    "lbs_to_kg": ["lbs"],
}
# planning dataset: (задача, ожидаемые вызовы с правильными значениями параметров)
DATASET = [
    ("price of the best-selling product last week", [("get_today_date", {}), ("fetch_top_products", {"start_date": "09-07", "end_date": "09-13", "num_products": 1}), ("fetch_product_info", {"product_name": "Fruity Fedora"})]),
    ("what is today's date", [("get_today_date", {})]),
    ("info about Fruity Fedora", [("fetch_product_info", {"product_name": "Fruity Fedora"})]),
    ("convert 40 lbs to kg", [("lbs_to_kg", {"lbs": 40})]),
    ("top 3 products last week", [("get_today_date", {}), ("fetch_top_products", {"start_date": "09-07", "end_date": "09-13", "num_products": 3})]),
    ("weight of the top product in kg", [("get_today_date", {}), ("fetch_top_products", {"start_date": "09-07", "end_date": "09-13", "num_products": 1}), ("lbs_to_kg", {"lbs": 2})]),
]
K = 5  # сколько планов просим у агента на каждую задачу
# mock: вероятности ошибок на вызов (сложные tools с несколькими параметрами ошибаются чаще)
P_ERR = {"get_today_date": (0.02, 0.0, 0.0), "fetch_top_products": (0.05, 0.15, 0.25),
         "fetch_product_info": (0.05, 0.05, 0.10), "lbs_to_kg": (0.03, 0.05, 0.10)}  # (invalid tool, bad params, wrong value)
rng = random.Random(2024)


def mock_plan(expected):
    """Агент пытается воспроизвести ожидаемый план, но иногда ломает вызов."""
    plan = []
    for name, args in expected:
        r = rng.random()
        p_tool, p_param, p_value = P_ERR[name]
        if r < p_tool:
            plan.append(("bing_search", {"q": name}))                       # invalid tool
        elif r < p_tool + p_param:
            plan.append((name, {**args, "extra": 1}))                       # valid tool, invalid params
        elif r < p_tool + p_param + p_value and args:
            k = next(iter(args))
            plan.append((name, {**args, k: "WRONG" if isinstance(args[k], str) else args[k] + 1}))  # wrong value
        else:
            plan.append((name, dict(args)))
    return plan


def classify_call(call, expected_call):
    name, args = call
    if name not in INVENTORY:
        return "invalid tool"
    if set(args) != set(INVENTORY[name]):
        return "valid tool, invalid params"
    if call != expected_call:
        return "valid tool, wrong values"
    return "ok"


print("\n== 2. Planning dataset: K планов на задачу, считаем метрики")
call_kinds, by_tool, plan_ok, attempts_to_valid, unsolved = Counter(), defaultdict(Counter), 0, [], 0
for task, expected in DATASET:
    first_valid = None
    for i in range(1, K + 1):
        plan = mock_plan(expected)
        kinds = [classify_call(c, e) for c, e in zip(plan, expected)]
        for (_, exp_call), kind in zip(zip(plan, expected), kinds):
            call_kinds[kind] += 1
            by_tool[exp_call[0]][kind] += 1  # ошибку записываем на tool, который агент должен был вызвать
        if all(k == "ok" for k in kinds):
            plan_ok += 1
            first_valid = first_valid or i
    if first_valid:
        attempts_to_valid.append(first_valid)
    else:
        unsolved += 1
total_plans, total_calls = len(DATASET) * K, sum(call_kinds.values())
print(f"планов всего: {total_plans}, валидных: {plan_ok} ({plan_ok / total_plans:.0%})")
print(f"среднее число планов до первого валидного (по решённым задачам): {sum(attempts_to_valid) / len(attempts_to_valid):.2f}; задач без валидного плана: {unsolved}")
print(f"вызовов всего: {total_calls}, валидных: {call_kinds['ok']} ({call_kinds['ok'] / total_calls:.0%})")
for kind in ("invalid tool", "valid tool, invalid params", "valid tool, wrong values"):
    print(f"  {kind:28s} {call_kinds[kind]:>3} ({call_kinds[kind] / total_calls:.0%})")
print("ошибки по tools (где модели труднее всего):")
for name, c in sorted(by_tool.items(), key=lambda x: -(sum(x[1].values()) - x[1]["ok"])):
    bad = sum(c.values()) - c["ok"]
    print(f"  {name:20s} ошибок {bad:>2} из {sum(c.values()):>2} вызовов")
print("Tool с самой высокой долей ошибок — кандидат на упрощение: лучше описание, больше примеров или другой tool.")

print("\n== 3. Ablation: убираем tool и смотрим, падает ли качество")
# для каждой задачи: какие наборы tools достаточны (альтернативные способы решить)
TASKS = {
    "цена хита недели": [{"get_today_date", "fetch_top_products", "fetch_product_info"}, {"sql_executor"}],
    "дата": [{"get_today_date"}],
    "инфо о товаре": [{"fetch_product_info"}, {"sql_executor"}],
    "фунты в кг": [{"lbs_to_kg"}, {"calculator"}],
    "топ-3 за неделю": [{"get_today_date", "fetch_top_products"}, {"sql_executor"}],
    "курс валют": [{"web_search"}],
}
ALL_TOOLS = set().union(*[s for sets in TASKS.values() for s in sets]) | {"image_captioner"}


def pass_rate(tools):
    return sum(any(s <= tools for s in sets) for sets in TASKS.values()) / len(TASKS)


base = pass_rate(ALL_TOOLS)
print(f"все tools: {base:.0%} задач решаются")
for t in sorted(ALL_TOOLS):
    rate = pass_rate(ALL_TOOLS - {t})
    verdict = "можно убрать" if rate == base else f"нужен (качество падает на {base - rate:.0%})"
    print(f"  без {t:20s}: {rate:.0%} -> {verdict}")
print("image_captioner не нужен ни одной задаче: лишний tool только занимает место в контексте.")

print("\n== 4. Какие tools вызывают чаще и какие идут друг за другом")
TRACES = [["get_today_date", "fetch_top_products", "fetch_product_info"]] * 5 + [["fetch_product_info"]] * 3 + \
         [["get_today_date", "fetch_top_products"]] * 3 + [["lbs_to_kg"]] * 2
calls = Counter(t for tr in TRACES for t in tr)
print("частота вызовов:", dict(calls.most_common()))
pairs = Counter((a, b) for tr in TRACES for a, b in zip(tr, tr[1:]))
nexts = Counter(a for tr in TRACES for a in tr[:-1])
for (a, b), n in pairs.most_common():
    print(f"  после {a} -> {b}: вероятность {n / nexts[a]:.2f}")
print("Пара get_today_date -> fetch_top_products идёт всегда вместе: её можно слить в один tool «топ товаров за неделю».")

print("\n== 5. Эффективность: сравнение агента с человеком")
runs = {"агент": [(6, 0.12, 40), (9, 0.20, 65), (5, 0.10, 35), (14, 0.35, 110)],
        "человек": [(8, 0.0, 600), (6, 0.0, 480), (7, 0.0, 520), (9, 0.0, 700)]}  # (шагов, $, секунд)
for who, rs in runs.items():
    n = len(rs)
    print(f"{who:8s}: шагов {sum(r[0] for r in rs) / n:.1f}, цена ${sum(r[1] for r in rs) / n:.2f}, время {sum(r[2] for r in rs) / n:.0f} с")
print("Цифры условные. Агент быстрее, но платит за API. Человек медленнее, зато без прямой цены. Сравнивайте обе оси.")
print("И помните: что просто человеку, может быть дорого агенту, и наоборот.")

print("\n== 6. Intent classifier: сначала понять, чего хотят, и отсеять чужие запросы")


def classify_intent(query):
    q = query.lower()
    if any(w in q for w in ("invoice", "payment", "charge")):
        return "billing"
    if any(w in q for w in ("password", "login", "sign in")):
        return "account"
    return "IRRELEVANT"


TOOLS_BY_INTENT = {"billing": ["fetch_recent_payments"], "account": ["search_docs"], "IRRELEVANT": []}
for q in ("Why was I charged twice?", "How do I reset my password?", "Write a poem about the sea"):
    intent = classify_intent(q)
    action = "вежливо отказать, не тратя вычисления" if intent == "IRRELEVANT" else f"дать агенту tools {TOOLS_BY_INTENT[intent]}"
    print(f"{q!r:36s} -> {intent:10s} -> {action}")
