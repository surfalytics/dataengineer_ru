"""Глава 4: оценка instruction-following. Два стиля.
1) IFEval-стиль: инструкции, которые проверяет код (ключевые слова, длина, JSON, число пунктов).
2) INFOBench-стиль: для каждой инструкции список вопросов да/нет, на них отвечает судья.
   Здесь судья заменён готовыми ответами. В настоящей системе их даёт человек или AI judge.
3) Как отличить плохое следование инструкции от плохого знания предметной области.
Ответы «моделей» заданы вручную, поэтому вывод повторяется.
Запуск: python3 scripts/ai-engineering-code/ch04_instruction_following.py   (только стандартная библиотека)"""
import json
import re

# ---------- 1. проверки, которые делает код ----------
def has_keywords(text, words):
    return all(w.lower() in text.lower() for w in words)

def no_forbidden(text, words):
    return not any(w.lower() in text.lower() for w in words)

def max_words(text, n):
    return len(text.split()) <= n

def bullet_count(text, n):
    return len(re.findall(r"^\* ", text, flags=re.M)) == n

def is_json(text, _=None):
    try:
        json.loads(text)
        return True
    except ValueError:
        return False

CHECKS = {"keywords": has_keywords, "forbidden": no_forbidden, "max_words": max_words,
          "bullets": bullet_count, "json": is_json}

# (prompt, инструкция, параметр, ответ model-a, ответ model-b)
CASES = [
    ("Напиши фразу про данные", "keywords", ["pipeline", "данные"],
     "Данные идут через pipeline каждую ночь.", "Данные текут через pipeline."),
    ("Опиши dbt без слова «magic»", "forbidden", ["magic"],
     "dbt собирает модели из SQL.", "dbt — это magic для аналитиков."),
    ("Ответь не больше чем в 8 слов", "max_words", 8,
     "dbt превращает SQL-запросы в тестируемые модели и ещё добавляет документацию.", "dbt превращает SQL в модели."),
    ("Дай ровно 3 пункта", "bullets", 3,
     "* загрузка\n* очистка\n* отчёт", "* загрузка\n* очистка\n* отчёт\n* алерты"),
    ("Верни ответ в JSON", "json", None,
     '{"status": "ok", "rows": 120}', 'Вот JSON: {"status": "ok"}'),
]

print("== 1. Проверки кода (IFEval-стиль)")
scores = {"model-a": [], "model-b": []}
for prompt, name, param, out_a, out_b in CASES:
    res = []
    for model, out in (("model-a", out_a), ("model-b", out_b)):
        ok = CHECKS[name](out, param)
        scores[model].append(ok)
        res.append(f"{model}={'OK' if ok else 'FAIL'}")
    print(f"{name:10s} {'  '.join(res)}")
for model, s in scores.items():
    print(f"{model}: выполнено {sum(s)} из {len(s)} инструкций = {sum(s) / len(s):.0%}")

# ---------- 2. чек-листы да/нет (INFOBench-стиль) ----------
# инструкция -> список вопросов; ответы судьи (True = да) для двух моделей
CHECKLISTS = {
    "Составь опросник, который поможет гостям отеля писать отзывы": {
        "criteria": ["Это опросник?", "Он предназначен для гостей отеля?", "Он помогает писать отзыв?"],
        "model-a": [True, True, True], "model-b": [True, True, False]},
    "Объясни дедупликацию языком для школьника": {
        "criteria": ["Текст про дедупликацию?", "Язык подходит школьнику?"],
        "model-a": [True, False], "model-b": [True, True]},
    "Напиши письмо вежливым тоном и без технических терминов": {
        "criteria": ["Это письмо?", "Тон вежливый?", "Нет технических терминов?"],
        "model-a": [True, True, False], "model-b": [True, True, True]},
}

print("\n== 2. Чек-листы да/нет (INFOBench-стиль)")
for model in ("model-a", "model-b"):
    per_instruction = [sum(c[model]) / len(c[model]) for c in CHECKLISTS.values()]
    strict = [all(c[model]) for c in CHECKLISTS.values()]
    yes = sum(sum(c[model]) for c in CHECKLISTS.values())
    total = sum(len(c[model]) for c in CHECKLISTS.values())
    print(f"{model}: по инструкциям {[f'{x:.2f}' for x in per_instruction]}, "
          f"итог = {yes}/{total} критериев = {yes / total:.0%}, "
          f"инструкций выполнено полностью: {sum(strict)} из {len(strict)}")

# ---------- 3. формат или предметная область? ----------
ALLOWED = {"NEGATIVE", "POSITIVE", "NEUTRAL"}
TRUTH = ["POSITIVE", "NEGATIVE", "NEGATIVE", "NEUTRAL", "POSITIVE", "NEGATIVE"]
ANSWERS = ["POSITIVE", "ANGRY", "NEGATIVE", "NEUTRAL", "HAPPY", "ANGRY"]  # «ANGRY» и «HAPPY» — вне инструкции

print("\n== 3. Классификация тональности: формат или предметная область?")
valid = [a for a in ANSWERS if a in ALLOWED]
format_errors = len(ANSWERS) - len(valid)
correct = sum(a == t for a, t in zip(ANSWERS, TRUTH))
correct_valid = sum(a == t for a, t in zip(ANSWERS, TRUTH) if a in ALLOWED)
print(f"ответов вне списка меток: {format_errors} из {len(ANSWERS)} (проблема instruction-following)")
print(f"accuracy на всех ответах: {correct / len(ANSWERS):.0%}")
print(f"accuracy среди допустимых ответов: {correct_valid / len(valid):.0%} (проблема предметной области: здесь её нет)")
print("Вывод: модель понимает тональность, но не держит формат. Жалуйтесь на prompt или на инструкцию, а не на знания.")
