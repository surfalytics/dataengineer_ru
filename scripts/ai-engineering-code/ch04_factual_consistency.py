"""Глава 4: factual consistency на игрушечных данных. Три идеи.
1) SAFE-стиль: ответ делим на утверждения, делаем их самодостаточными, проверяем поиском по базе фактов.
2) SelfCheckGPT-стиль: те же вопросы задаём модели несколько раз. Утверждение, которое повторяется редко, подозрительно.
3) Textual entailment: пара (контекст, гипотеза) даёт одну из трёх меток.
Поиск, «модель» и ответы здесь заменены простыми правилами и готовыми строками.
В настоящей системе вы замените функции на вызовы LLM и поискового API.
Запуск: python3 scripts/ai-engineering-code/ch04_factual_consistency.py   (только стандартная библиотека)"""
import re

STOP = {"в", "и", "—", "он", "она", "который"}
KB = [  # маленькая «поисковая база» фактов
    "Python — язык программирования",
    "Python создан Гвидо ван Россумом",
    "Python впервые выпущен в 1991 году",
    "Берлин — столица Германии",
]
TOPIC = "Python"
ANSWER = "Python — язык программирования. Он создан Гвидо ван Россумом. Он впервые выпущен в 1950 году. Берлин — столица Германии."


def words(text):
    return {w for w in re.findall(r"[\w-]+", text.lower()) if w not in STOP}


def numbers(text):
    return set(re.findall(r"\d+", text))


# ---------- 1. SAFE-стиль ----------
def split_claims(answer):          # шаг 1: на отдельные утверждения
    return [s.strip() for s in answer.split(".") if s.strip()]


def make_self_contained(claim):    # шаг 2: «Он» -> тема, чтобы утверждение читалось без контекста
    return re.sub(r"^(Он|Она|Оно) ", TOPIC + " ", claim)


def is_relevant(claim):            # шаг 3: относится ли утверждение к вопросу
    return TOPIC.lower() in claim.lower()


def search_supports(claim):        # шаг 4: «поиск» по базе фактов
    cw, cn = words(claim), numbers(claim)
    for fact in KB:
        jaccard = len(cw & words(fact)) / len(cw | words(fact))
        if jaccard >= 0.6 and cn <= numbers(fact):   # слова похожи и числа не противоречат
            return True
    return False


print("== 1. SAFE-стиль: вопрос «Что такое Python?»")
verdicts = {"подтверждено": 0, "не подтверждено": 0, "нерелевантно": 0}
for raw in split_claims(ANSWER):
    claim = make_self_contained(raw)
    if not is_relevant(claim):
        verdict = "нерелевантно"
    else:
        verdict = "подтверждено" if search_supports(claim) else "не подтверждено"
    verdicts[verdict] += 1
    print(f"{verdict:16s} | {claim}")
print("итог:", verdicts)

# ---------- 2. SelfCheck-стиль ----------
SAMPLES = [  # «ещё пять ответов модели на тот же вопрос»
    "Python — язык программирования. Python создан Гвидо ван Россумом. Python впервые выпущен в 1991 году.",
    "Python — язык программирования. Python создан Гвидо ван Россумом. Первый релиз вышел в 1991 году.",
    "Python — язык программирования, который придумал Гвидо ван Россум.",
    "Python — язык программирования. Python создан Гвидо ван Россумом. Python впервые выпущен в 1950 году.",
    "Python — язык программирования. Python создан Гвидо ван Россумом.",
]

print("\n== 2. SelfCheck-стиль: как часто утверждение повторяют другие ответы")
for raw in split_claims(ANSWER)[:3]:
    claim = make_self_contained(raw)
    seen = sum(words(claim) <= words(s) for s in SAMPLES)
    flag = "ПОДОЗРИТЕЛЬНО" if seen / len(SAMPLES) < 0.5 else "ok"
    print(f"{seen}/{len(SAMPLES)} {flag:14s} | {claim}")
print(f"цена: {len(SAMPLES) + 1} вызовов модели на один ответ (SAFE дороже: поиск на каждое утверждение)")

# ---------- 3. Textual entailment ----------
FRUITS = {"яблоки", "апельсины", "груши"}


def entailment(premise, hypothesis):
    """Правило только для контекста «Мария любит все фрукты»."""
    m = re.match(r"Мария (любит|ненавидит) (\w+)", hypothesis)
    if m and m.group(2) in FRUITS:
        return "entailment" if m.group(1) == "любит" else "contradiction"
    return "neutral"


SCORE_3 = {"entailment": 1, "neutral": 0, "contradiction": -1}   # шкала из трёх значений
SCORE_2 = {"entailment": 1, "neutral": 0, "contradiction": 0}    # бинарная шкала

print("\n== 3. Textual entailment: контекст «Мария любит все фрукты»")
for h in ["Мария любит яблоки", "Мария ненавидит апельсины", "Мария любит рыбу"]:
    label = entailment("Мария любит все фрукты", h)
    print(f"{label:13s} шкала(-1/0/1)={SCORE_3[label]:2d} бинарная={SCORE_2[label]} | {h}")
