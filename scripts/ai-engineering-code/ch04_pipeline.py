"""Глава 4: мини-pipeline оценки на примере «достать работодателя из PDF-резюме».
1) Оценка по компонентам: шаг A (PDF -> текст) и шаг B (текст -> работодатель) измеряем отдельно и вместе.
2) Per turn и per task: качество каждого ответа и решена ли задача.
3) Дешёвая проверка на всех данных и дорогая на малой доле. Уверенность по logprobs.
4) Журнал запуска: что нужно логировать, чтобы результаты можно было сравнить.
Шаги pipeline здесь простые функции с шумом, а не настоящие модели. Запуск: python3 scripts/ai-engineering-code/ch04_pipeline.py
(только стандартная библиотека)"""
import hashlib
import json
import random
from difflib import SequenceMatcher

rng = random.Random(17)

# ---------- данные: 40 «резюме» ----------
EMPLOYERS = ["Acme Data", "Nordwind", "Blue Tractor", "Kappa Retail", "Lumen Bank", "Orbit Cloud"]
LAYOUTS = ["one-column"] * 20 + ["two-columns"] * 12 + ["scan"] * 8
NOISE = {"one-column": 0.0, "two-columns": 0.03, "scan": 0.10}   # доля испорченных символов на шаге A
resumes = []
for i, layout in enumerate(LAYOUTS):
    employer = rng.choice(EMPLOYERS)
    label = rng.choice(["Текущий работодатель", "Текущий работодатель", "Текущий работодатель", "Работает в"])
    text = f"Резюме №{i}. Опыт 7 лет. {label}: {employer}. Навыки: SQL, Python, dbt."
    resumes.append(dict(id=i, layout=layout, truth_text=text, employer=employer))


def step_a_pdf_to_text(r):
    """Шаг A: портим часть символов. Двухколоночный PDF и скан портятся сильнее."""
    p = NOISE[r["layout"]]
    return "".join(c if rng.random() >= p else "#" for c in r["truth_text"])


def step_b_extract_employer(text):
    """Шаг B: знает только формат «Текущий работодатель: X»."""
    for line in text.split(". "):
        if line.startswith("Текущий работодатель: "):
            return line.split(": ", 1)[1].strip()
    return None


# ---------- 1. оценка по компонентам ----------
rows = []
for r in resumes:
    text = step_a_pdf_to_text(r)
    sim = SequenceMatcher(None, text, r["truth_text"]).ratio()
    employer = step_b_extract_employer(text)
    text_ok = r["employer"] in text and ("Текущий работодатель:" in text or "Работает в:" in text)
    rows.append(dict(layout=r["layout"], sim=sim, text_ok=text_ok, found=employer, truth=r["employer"]))

print("== 1. Компоненты по отдельности")
print(f"шаг A: средняя похожесть текста {sum(x['sim'] for x in rows) / len(rows):.3f}")
good_text = [x for x in rows if x["text_ok"]]
print(f"шаг B: accuracy на верно извлечённом тексте = {sum(x['found'] == x['truth'] for x in good_text) / len(good_text):.0%} ({len(good_text)} резюме)")
print(f"сквозная accuracy: {sum(x['found'] == x['truth'] for x in rows) / len(rows):.0%} ({len(rows)} резюме)")
print("\nпо типу файла (срез):")
for layout in ["one-column", "two-columns", "scan"]:
    part = [x for x in rows if x["layout"] == layout]
    print(f"  {layout:12s} похожесть {sum(x['sim'] for x in part) / len(part):.3f}  "
          f"верный работодатель {sum(x['found'] == x['truth'] for x in part) / len(part):.0%}")
print("Падение у two-columns и scan говорит о шаге A. Ошибки в one-column — о шаге B (формат «Работает в»).")

# ---------- 2. per turn и per task ----------
# (ход, оценка ответа 1-5), решена ли задача за разговор
TASKS = {"A": ([4, 4], True), "B": ([5, 4, 4, 3, 3, 4, 4], True), "C": ([4, 3, 2], False), "D": ([5, 5], True)}
print("\n== 2. Per turn и per task")
all_turns = [s for scores, _ in TASKS.values() for s in scores]
solved = [(len(s), ok) for s, ok in TASKS.values() if ok]
print(f"per turn: средняя оценка ответа {sum(all_turns) / len(all_turns):.2f} из 5 ({len(all_turns)} ходов)")
print(f"per task: решено {len(solved)} из {len(TASKS)}, в среднем за {sum(n for n, _ in solved) / len(solved):.1f} хода")
print("Задача B решена, но за 7 ходов; задача C не решена. Оценки отдельных ответов этого не показывают.")

# ---------- 3. дешёвая проверка на всём, дорогая на 1% ----------
ANSWERS_PER_DAY = 10_000
CHEAP, EXPENSIVE = 0.0001, 0.02    # $ за одну проверку: классификатор и AI judge
print("\n== 3. Сколько стоит проверка за день")
print(f"AI judge на всех ответах:        ${ANSWERS_PER_DAY * EXPENSIVE:8.2f}")
combo = ANSWERS_PER_DAY * CHEAP + ANSWERS_PER_DAY * 0.01 * EXPENSIVE
print(f"классификатор на всех + judge на 1%: ${combo:8.2f}  ({ANSWERS_PER_DAY * EXPENSIVE / combo:.0f} раз дешевле)")

print("\nУверенность по logprobs для классификатора с тремя классами:")
for probs in ([0.95, 0.03, 0.02], [0.36, 0.33, 0.31]):
    print(f"  вероятности классов {probs}: {'уверена' if max(probs) >= 0.6 else 'НЕ уверена, отправить на ручную проверку'}")

# ---------- 4. журнал запуска ----------
def run_record(config):
    blob = json.dumps(config, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(blob.encode()).hexdigest()[:10]


config = {"eval_set": "resumes_v3", "rubric": "v2", "judge_model": "judge-large-2025-01", "judge_temperature": 0,
          "judge_prompt_sha": "a1b2c3", "n_examples": len(resumes)}
print("\n== 4. Журнал запуска")
print("run_id", run_record(config), config)
config["judge_temperature"] = 0.7
print("run_id", run_record(config), "<- изменили temperature судьи: это уже другой запуск, прямое сравнение невозможно")
