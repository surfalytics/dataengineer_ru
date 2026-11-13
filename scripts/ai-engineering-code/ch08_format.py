#!/usr/bin/env python3
"""Глава 8: формат данных для finetuning: из few-shot prompt в примеры, chat template, JSONL. Без внешних библиотек.

Что показывает скрипт:
  1. Few-shot prompt для базовой модели превращаем в обучающие примеры. После finetuning prompt короче.
  2. Один пример записываем в трёх форматах: prompt/completion, chat messages (JSONL), текст по шаблону.
  3. Проверка записей перед обучением: роли, пустые поля, лишние пробелы, HTML, длина.
  4. Проверка prompt на inference: совпадает ли он с форматом обучения.
  5. Формат для tool use: одно сообщение модели может идти не пользователю, а инструменту.
Шаблоны здесь наши, упрощённые. Настоящий chat template берите у токенизатора вашей модели.

Запуск из корня репозитория: python3 -I scripts/ai-engineering-code/ch08_format.py
"""
import json
import re

# ---------- 1. Few-shot prompt -> обучающие примеры ----------
FEW_SHOT = """Определи, съедобно ли.

Предмет: бургер
Ответ: съедобно

Предмет: машина
Ответ: несъедобно

Предмет: гриб
Ответ: съедобно

Предмет: {INPUT}
Ответ:"""
examples = [("бургер", "съедобно"), ("машина", "несъедобно"), ("гриб", "съедобно"),
            ("шарф", "несъедобно"), ("сыр", "съедобно")]


def rough_tokens(text):
    """Грубая оценка числа токенов: слова и знаки. Настоящий токенизатор даст другое число."""
    return len(re.findall(r"\w+|[^\w\s]", text))


tuned_prompt = "{INPUT} -->"
base_cost = rough_tokens(FEW_SHOT.format(INPUT="яблоко"))
tuned_cost = rough_tokens(tuned_prompt.format(INPUT="яблоко"))
print("=== 1. Prompt до и после finetuning ===")
print(f"Few-shot prompt для базовой модели: около {base_cost} токенов на запрос")
print(f"Prompt после finetuning («яблоко -->»): около {tuned_cost} токенов на запрос")
calls = 1_000_000
price_per_million = 0.50     # условная цена, $ за 1 млн входных токенов
saved = (base_cost - tuned_cost) * calls / 1e6 * price_per_million
print(f"Экономия на {calls:,} запросов при условных ${price_per_million:.2f} за 1M токенов: ${saved:.2f}".replace(",", " "))
print("Но finetuning стоит денег и времени. Экономия на prompt это один из аргументов, не единственный.")

# ---------- 2. Три формата одного примера ----------
SYSTEM = "Ты классификатор. Отвечай одним словом."
item, label = examples[0]
pc = {"prompt": f"{item} -->", "completion": f" {label}"}
chat = {"messages": [{"role": "system", "content": SYSTEM},
                     {"role": "user", "content": item},
                     {"role": "assistant", "content": label}]}


def render_chatml(msgs):
    return "".join(f"<|im_start|>{m['role']}\n{m['content']}<|im_end|>\n" for m in msgs)


def render_inst(msgs):
    sys_msg = next(m["content"] for m in msgs if m["role"] == "system")
    user = next(m["content"] for m in msgs if m["role"] == "user")
    asst = next(m["content"] for m in msgs if m["role"] == "assistant")
    return f"<<SYS>>{sys_msg}<</SYS>> [INST] {user} [/INST] {asst}</s>"


print("\n=== 2. Один пример, три формата ===")
print("prompt/completion (строка JSONL):")
print(" ", json.dumps(pc, ensure_ascii=False))
print("chat messages (строка JSONL):")
print(" ", json.dumps(chat, ensure_ascii=False))
print("Текст по шаблону «chatml»:")
print("  " + render_chatml(chat["messages"]).rstrip("\n").replace("\n", "\n  "))
print("Текст по шаблону «inst»:")
print(" ", render_inst(chat["messages"]))
print("Шаблоны разные. Модель, обученная на одном, на другом работает хуже: токены-разделители для неё чужие.")


# ---------- 3. Проверка записей перед обучением ----------
def validate(rec, max_tokens=60):
    errs = []
    msgs = rec.get("messages", [])
    roles = [m.get("role") for m in msgs]
    if not msgs or roles[-1] != "assistant":
        errs.append("последнее сообщение не от assistant")
    body = [r for r in roles if r != "system"]
    if any(a == b for a, b in zip(body, body[1:])):
        errs.append("роли user/assistant не чередуются")
    for m in msgs:
        c = m.get("content", "")
        if not c.strip():
            errs.append("пустое сообщение")
        if c != c.strip():
            errs.append("пробелы по краям")
        if re.search(r"<[a-z]+[^>]*>", c):
            errs.append("HTML-теги в тексте")
    if sum(rough_tokens(m.get("content", "")) for m in msgs) > max_tokens:
        errs.append("слишком длинная запись")
    return sorted(set(errs))


def rec(*pairs):
    return {"messages": [{"role": r, "content": c} for r, c in pairs]}


dataset = [
    rec(("user", "гриб"), ("assistant", "съедобно")),
    rec(("user", "сыр"), ("assistant", "съедобно ")),
    rec(("user", "<b>шарф</b>"), ("assistant", "несъедобно")),
    rec(("user", "машина"), ("user", "ещё раз"), ("assistant", "несъедобно")),
    rec(("user", "торт"), ("assistant", "")),
    rec(("user", "яблоко"),),
]
print("\n=== 3. Проверка записей ===")
for i, r in enumerate(dataset):
    e = validate(r)
    print(f"  запись {i}: {'ok' if not e else '; '.join(e)}")
bad = sum(1 for r in dataset if validate(r))
print(f"Плохих записей: {bad} из {len(dataset)}")

# ---------- 4. Проверка prompt на inference ----------
TRAIN_FORMAT = re.compile(r"[\w-]+ -->")
print("\n=== 4. Prompt на inference должен совпадать с форматом обучения («слово -->») ===")
for p in ["burger -->", "burger", "Item: burger -->", "burger --> "]:
    ok = bool(TRAIN_FORMAT.fullmatch(p))
    print(f"  {p!r:<22} {'ok' if ok else 'формат нарушен'}")

# ---------- 5. Формат для tool use ----------
tool_record = {"messages": [
    {"role": "user", "content": "Посчитай средний чек за март и напиши коротко."},
    {"role": "assistant", "to": "python", "content": "df[df.month == 3].amount.mean()"},
    {"role": "tool", "from": "python", "content": "1840.5"},
    {"role": "assistant", "to": "user", "content": "Средний чек за март: 1840,5."},
]}
print("\n=== 5. Tool use: у сообщения есть адресат ===")
for m in tool_record["messages"]:
    route = f"{m.get('from', m['role'])} -> {m.get('to', 'модель')}"
    print(f"  {route:<22} {m['content']}")
