"""Глава 5: сборка prompt из частей, формат примеров и chat template.
Что показывает:
 1. prompt из частей: роль, описание задачи, формат ответа, примеры, контекст, сама задача;
 2. два формата few-shot примеров и разница в токенах;
 3. chat template: одна пара (system, user) даёт разный итоговый текст для двух моделей;
 4. проверка итогового prompt до отправки: не тот шаблон, лишняя пустая строка, маркер во входе.
Токены считаем грубо (слово или группа знаков = 1 токен). Настоящий токенизатор даст другие числа.
Запуск: python3 -I scripts/ai-engineering-code/ch05_prompt_builder.py   (только стандартная библиотека)"""
import re
from dataclasses import dataclass, field


def count_tokens(text):
    """Грубая оценка числа токенов: слово или группа знаков препинания."""
    return len(re.findall(r"\w+|[^\w\s]+", text))


@dataclass
class Example:
    inp: str
    out: str


@dataclass
class PromptSpec:
    role: str                 # persona: кем притворяется модель
    task: str                 # что сделать
    output_format: str        # как оформить ответ
    examples: list = field(default_factory=list)


# --- 1. Сборка prompt ------------------------------------------------------------------------
STYLES = {
    # стиль: (как писать пример, как закончить prompt, маркер конца ввода)
    "verbose": ("Вход: {inp}\nВыход: {out}", "Вход: {q}\nВыход:", "Выход:"),
    "compact": ("{inp} --> {out}", "{q} -->", "-->"),
}


def system_text(spec):
    return f"{spec.role}\n{spec.task}\n{spec.output_format}"


def user_text(spec, question, context="", style="verbose"):
    ex_fmt, last_fmt, marker = STYLES[style]
    if marker in question:  # маркер конца не должен встречаться во вводе: иначе модель запутается
        raise ValueError(f"маркер {marker!r} встречается во входных данных")
    parts = []
    if spec.examples:
        parts.append("Примеры:\n" + "\n".join(ex_fmt.format(inp=e.inp, out=e.out) for e in spec.examples))
    if context:
        parts.append("Контекст:\n" + context)
    parts.append(last_fmt.format(q=question))
    return "\n\n".join(parts)


# --- 2. Chat template: у каждой модели свой ---------------------------------------------------
TEMPLATES = {
    "llama2": "<s>[INST] <<SYS>>\n{system}\n<</SYS>>\n\n{user} [/INST]",
    "llama3": ("<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{system}<|eot_id|>"
               "<|start_header_id|>user<|end_header_id|>\n\n{user}<|eot_id|>"
               "<|start_header_id|>assistant<|end_header_id|>\n\n"),
}
REQUIRED = {
    "llama2": ["<s>[INST] <<SYS>>", "<</SYS>>", "[/INST]"],
    "llama3": ["<|begin_of_text|>", "<|start_header_id|>system<|end_header_id|>", "<|eot_id|>",
               "<|start_header_id|>assistant<|end_header_id|>"],
}


def render_chat(model, system, user):
    # replace, а не format: в тексте prompt могут быть фигурные скобки
    return TEMPLATES[model].replace("{system}", system).replace("{user}", user)


def check_prompt(final, model):
    """Возвращает список проблем. Пустой список = prompt похож на ожидаемый шаблон."""
    problems = [f"нет обязательного куска {m!r}" for m in REQUIRED[model] if m not in final]
    for other, markers in REQUIRED.items():
        if other != model and any(m in final for m in markers):
            problems.append(f"в тексте остались метки шаблона {other}")
    if "\n\n\n" in final:
        problems.append("есть лишняя пустая строка (три перевода строки подряд)")
    return problems


def show(text):
    """Печатаем prompt так, чтобы были видны переводы строк."""
    return text.replace("\n", "¶\n")


# --- Демонстрация -----------------------------------------------------------------------------
spec = PromptSpec(
    role="Ты помощник аналитика. Ты отвечаешь по описаниям таблиц из каталога данных.",
    task="Назови таблицу, где лежат нужные данные. Если подходящей таблицы нет, напиши: нет данных.",
    output_format="Ответь одной строкой, только имя таблицы, без вступлений.",
    examples=[Example("Где лежат данные о возвратах?", "sales.returns"),
              Example("Где данные о погоде?", "нет данных")],
)
context = ("sales.orders: заказы, одна строка на заказ\n"
           "sales.returns: возвраты, одна строка на возврат\n"
           "crm.customers: клиенты")
question = "Где хранятся заказы?"

print("== 1. Части prompt")
sys_t = system_text(spec)
usr_t = user_text(spec, question, context)
print("-- system prompt --")
print(sys_t)
print("-- user prompt --")
print(usr_t)
print(f"токенов (грубо): system={count_tokens(sys_t)}, user={count_tokens(usr_t)}, всего={count_tokens(sys_t + usr_t)}")

print("\n== 2. Итоговый текст для модели зависит от шаблона")
for model in TEMPLATES:
    final = render_chat(model, "Переведи текст на французский.", "Как дела?")
    print(f"-- {model} --")
    print(show(final))
    print("проверка:", check_prompt(final, model) or "ok")

print("\n== 3. Формат примеров: verbose и compact (3 примера)")
mini = PromptSpec(role="", task="Отметь предмет как съедобный или несъедобный.", output_format="",
                  examples=[Example("нут", "съедобный"), Example("коробка", "несъедобный"),
                            Example("яблоко", "съедобный")])
for style in STYLES:
    text = mini.task + "\n" + user_text(mini, "пицца", style=style)
    print(f"-- {style}: {count_tokens(text)} токенов --")
    print(text)

print("\nЧисло токенов при росте числа примеров:")
pool = [Example("нут", "съедобный"), Example("коробка", "несъедобный"), Example("яблоко", "съедобный"),
        Example("камень", "несъедобный"), Example("сыр", "съедобный"), Example("книга", "несъедобный"),
        Example("рис", "съедобный"), Example("шина", "несъедобный"), Example("мёд", "съедобный"),
        Example("стекло", "несъедобный")]
print("примеров | verbose | compact")
for n in (0, 1, 3, 5, 10):
    row = []
    for style in STYLES:
        p = PromptSpec(role="", task=mini.task, output_format="", examples=pool[:n])
        row.append(count_tokens(p.task + "\n" + user_text(p, "пицца", style=style)))
    print(f"{n:>8} | {row[0]:>7} | {row[1]:>7}")

print("\n== 4. Ошибки, которые надо ловить до отправки")
final = render_chat("llama3", "Ты бот.", "Привет")
print("а) текст для llama3, но модель llama2:")
for p in check_prompt(final, "llama2"):
    print("  -", p)
bad = render_chat("llama2", "Ты бот.", "\nПривет")  # лишний перевод строки в начале user-сообщения
print("б) llama2 и лишний перевод строки в сообщении пользователя:")
print(show(bad))
for p in check_prompt(bad, "llama2"):
    print("  -", p)
good = render_chat("llama2", "Ты бот.", "Привет")
print("в) исправленный вариант:", check_prompt(good, "llama2") or "ok")
try:
    user_text(spec, "Что значит Выход: в таблице?")
except ValueError as e:
    print("г) ошибка маркера:", e)
