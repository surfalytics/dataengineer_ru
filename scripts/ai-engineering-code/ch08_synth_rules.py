#!/usr/bin/env python3
"""Глава 8: классические способы синтеза и аугментации данных. Без внешних библиотек.

Что показывает скрипт:
  1. Rule-based: шаблон транзакции + генератор значений (как Faker). Проверяем результат.
  2. Аугментация текста: замена слов на синонимы, перестановка гендерных слов (counterfactual).
  3. Perturbation: опечатки и замена 1,5% токенов случайными (как при обучении BERT).
  4. Simulation: симулируем редкое событие, чтобы выровнять классы.

Запуск из корня репозитория: python3 -I scripts/ai-engineering-code/ch08_synth_rules.py
"""
import random
from collections import Counter

rng = random.Random(2024)

# ---------- 1. Rule-based: шаблон + генератор ----------
MERCHANTS = {"супермаркет": (300, 6000), "кафе": (150, 2500), "такси": (200, 3500),
             "аптека": (100, 4000), "электроника": (2000, 90000)}
CITIES = ["Москва", "Казань", "Самара", "Омск", "Тверь"]
METHODS = ["карта", "карта", "карта", "наличные", "онлайн"]   # повтор = больший вес
STATUS = ["completed"] * 18 + ["pending"] + ["failed"]


def make_transaction(i):
    merchant = rng.choice(list(MERCHANTS))
    lo, hi = MERCHANTS[merchant]
    return {"id": f"T{i:05d}", "date": f"2024-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}",
            "amount": round(rng.uniform(lo, hi), 2), "merchant": merchant,
            "city": rng.choice(CITIES), "method": rng.choice(METHODS), "status": rng.choice(STATUS)}


tx = [make_transaction(i) for i in range(1, 2001)]
print("=== 1. Rule-based синтез: 2000 транзакций по шаблону ===")
for row in tx[:3]:
    print(" ", row)
checks = {"id уникальны": len({t["id"] for t in tx}) == len(tx),
          "суммы положительные": all(t["amount"] > 0 for t in tx),
          "статусы из списка": {t["status"] for t in tx} <= {"completed", "pending", "failed"}}
print("Проверки:", checks)
print("Доли статусов:", {k: round(v / len(tx), 3) for k, v in sorted(Counter(t["status"] for t in tx).items())})

# ---------- 2. Аугментация текста ----------
SYN = {"отличный": ["прекрасный", "замечательный"], "быстро": ["оперативно", "без задержек"],
       "помог": ["выручил", "оказал помощь"], "ответ": ["реакция", "отклик"]}
SWAP = {"она": "он", "он": "она", "её": "его", "его": "её", "мама": "папа", "папа": "мама",
        "сестра": "брат", "брат": "сестра", "Она": "Он", "Он": "Она"}


def synonym_aug(text):
    return " ".join(rng.choice(SYN[w]) if w in SYN else w for w in text.split())


def counterfactual(text):
    return " ".join(SWAP.get(w, w) for w in text.split())


print("\n=== 2. Аугментация текста ===")
src = "Она отличный врач и быстро помог пациенту"
print("Оригинал:         ", src)
print("Синонимы:         ", synonym_aug(src))
print("Counterfactual:   ", counterfactual(src))
src2 = "Сегодня мама готовит ужин, а её брат моет посуду"
print("Оригинал:         ", src2)
print("Counterfactual:   ", counterfactual(src2))
print("Замечание: падежи и рода сложнее. Для русского нужна морфология или LLM, словарь ломает грамматику.")


# ---------- 3. Perturbation ----------
def typo(word):
    if len(word) < 4:
        return word
    i = rng.randrange(1, len(word) - 2)
    kind = rng.choice(["swap", "drop"])
    return word[:i] + word[i + 1] + word[i] + word[i + 2:] if kind == "swap" else word[:i] + word[i + 1:]


def add_typos(text, rate=0.4):
    return " ".join(typo(w) if rng.random() < rate else w for w in text.split())


def random_token_replace(tokens, vocab, rate=0.015):
    return [rng.choice(vocab) if rng.random() < rate else t for t in tokens]


print("\n=== 3. Perturbation ===")
q = "как сбросить пароль от личного кабинета"
for _ in range(3):
    print("  опечатки:", add_typos(q))
vocab = ["заказ", "сервер", "кошка", "налог", "ветер"]
tokens = ("модель учится устойчивее если часть токенов заменить случайными " * 20).split()
changed = random_token_replace(tokens, vocab)
diff = sum(a != b for a, b in zip(tokens, changed))
print(f"  Заменили токенов: {diff} из {len(tokens)} ({100 * diff / len(tokens):.1f}%), цель 1,5%")

# ---------- 4. Simulation ----------
print("\n=== 4. Simulation: редкий класс ===")
FRAUD_RATE = 0.004
real = [rng.random() < FRAUD_RATE for _ in range(5000)]
print(f"Реальные данные: {sum(real)} мошеннических из {len(real)} ({100 * sum(real) / len(real):.2f}%)")


def simulate_fraud():
    """Правила, как выглядит мошенничество: ночь, крупная сумма, чужой город."""
    return {"hour": rng.choice([1, 2, 3, 4]), "amount": round(rng.uniform(20000, 90000), 2),
            "foreign_city": True, "is_fraud": True}


synthetic = [simulate_fraud() for _ in range(200)]
total_fraud = sum(real) + len(synthetic)
total = len(real) + len(synthetic)
print(f"После добавления {len(synthetic)} симулированных: {total_fraud} из {total} ({100 * total_fraud / total:.1f}%)")
print("Риск: модель выучит наши правила симуляции, а не настоящее мошенничество (проблема Sim2Real).")
