"""Глава 5: игрушечный автоподбор prompt по идее Promptbreeder: мутации, оценка на eval-данных, отбор лучших.
Модель здесь ненастоящая: mock_model() ведёт себя по простым правилам (см. функцию).
В настоящем инструменте вместо неё стоят вызовы API: и для оценки, и для мутаций.
Что показывает:
 1. цикл «мутировать -> оценить на eval-наборе -> оставить лучших»;
 2. сколько вызовов модели делает такой цикл, даже когда eval-набор маленький;
 3. почему нужен отдельный test-набор: оценка на dev завышена;
 4. что инструмент выбирает prompt, который лучше всего проходит именно вашу метрику (строгое сравнение строки).
Запуск: python3 -I scripts/ai-engineering-code/ch05_prompt_search.py   (только стандартная библиотека)"""
import random

LABELS = ["negative", "neutral", "positive"]
BASE = "Определи тональность сообщения клиента."
PARTS = {  # id части -> текст в prompt
    "role": "Ты опытный оператор поддержки.",
    "example": "Пример: «Всё сломалось» -> negative.",
    "one_word": "Ответь одним словом: negative, neutral или positive.",
    "no_preamble": "Без вступлений и пояснений.",
    "think": "Думай шаг за шагом.",
    "polite": "Пожалуйста, будь внимателен и вежлив.",
    "explain": "Объясни свой ответ подробно.",
}

# --- Данные: сообщения клиентов с известной тональностью (генерируем сами) ---------------------
PHRASES = {
    "negative": ["Всё сломалось", "Ужасный сервис", "Деньги не вернули", "Больше не буду заказывать"],
    "neutral": ["Когда будет доставка", "Какой у вас адрес", "Прошу прислать чек", "Где найти условия"],
    "positive": ["Спасибо за помощь", "Всё работает отлично", "Быстрая доставка", "Очень доволен"],
}
rng_data = random.Random(7)
DATA = []
for i in range(60):
    label = LABELS[i % 3]
    DATA.append((f"{rng_data.choice(PHRASES[label])} (заказ {1000 + i})", label))
rng_data.shuffle(DATA)
DEV, TEST = DATA[:30], DATA[30:]

CALLS = {"eval": 0, "mutate": 0}


def mock_model(prompt, message, true_label):
    """Правила игрушечной модели.
    1) качество определения тональности: 0,70 + 0,10 за роль + 0,10 за пример + 0,05 за «думай шаг за шагом»;
    2) формат: «объясни» ломает строгий ответ всегда; «одним словом» даёт чистый ответ;
       «без вступлений» помогает в 90% случаев; без указаний формата модель в 60% случаев пишет вступление."""
    CALLS["eval"] += 1
    rng = random.Random(f"{prompt}|{message}")
    p = 0.70 + 0.10 * ("Ты опытный" in prompt) + 0.10 * ("Пример:" in prompt) + 0.05 * ("шаг за шагом" in prompt)
    label = true_label if rng.random() < p else rng.choice([l for l in LABELS if l != true_label])
    if "Объясни" in prompt:
        return f"Потому что в тексте есть эмоция. Ответ: {label}"
    if "одним словом" in prompt:
        return label
    clean = 0.9 if "Без вступлений" in prompt else 0.4
    return label if rng.random() < clean else f"Думаю, это {label}"


def score(parts, dataset):
    prompt = " ".join([BASE] + [PARTS[p] for p in parts])
    return sum(mock_model(prompt, m, y).strip() == y for m, y in dataset) / len(dataset)  # строгое сравнение


# --- Мутации: тоже «вызовы модели» в настоящем инструменте ---------------------------------------
def mutate(parts, rng):
    CALLS["mutate"] += 1
    parts = list(parts)
    op = rng.choice(["add", "remove", "swap", "replace"])
    if op == "add" or not parts:
        free = [p for p in PARTS if p not in parts]
        if free:
            parts.insert(rng.randrange(len(parts) + 1), rng.choice(free))
    elif op == "remove":
        parts.pop(rng.randrange(len(parts)))
    elif op == "swap" and len(parts) > 1:
        i, j = rng.sample(range(len(parts)), 2)
        parts[i], parts[j] = parts[j], parts[i]
    else:
        free = [p for p in PARTS if p not in parts]
        if free:
            parts[rng.randrange(len(parts))] = rng.choice(free)
    return tuple(parts)


rng = random.Random(42)
cache = {}  # одинаковые prompts не оцениваем повторно: это экономит вызовы


def dev_score(parts):
    if parts not in cache:
        cache[parts] = score(parts, DEV)
    return cache[parts]


GENERATIONS, POP, KEEP = 5, 6, 2
population = [()]
print(f"eval-набор: dev {len(DEV)} примеров для поиска, test {len(TEST)} примеров отложены")
print(f"базовый prompt без добавок: dev {dev_score(()):.0%}")
for g in range(1, GENERATIONS + 1):
    parents = sorted(dict.fromkeys(population), key=dev_score, reverse=True)[:KEEP]  # без set: порядок не зависит от hash
    children = [mutate(rng.choice(parents), rng) for _ in range(POP - len(parents))]
    population = parents + children
    best = max(population, key=dev_score)
    print(f"поколение {g}: лучший dev {dev_score(best):.0%}, части {list(best) or '[]'}, "
          f"вызовов оценки {CALLS['eval']}, вызовов мутатора {CALLS['mutate']}")

best = max(cache, key=lambda k: (cache[k], -len(k)))
print("\nИтоговый prompt:")
print(" ".join([BASE] + [PARTS[p] for p in best]))
print(f"\ndev: {cache[best]:.0%}, test (не участвовал в поиске): {score(best, TEST):.0%}")
print(f"базовый prompt на test: {score((), TEST):.0%}")
total = CALLS["eval"] + CALLS["mutate"]
print(f"всего вызовов модели: {total} (оценка {CALLS['eval']} + мутации {CALLS['mutate']}); "
      f"это {len(cache)} разных prompts × {len(DEV)} примеров dev и ещё 2 прогона на test")
