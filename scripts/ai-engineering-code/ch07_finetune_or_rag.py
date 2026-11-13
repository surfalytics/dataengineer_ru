"""Глава 7: помощник «prompt, RAG или finetuning?». Правила взяты из главы, это не готовый продукт:
сначала оценка и prompt, потом тип ошибки (информационная или поведенческая), потом выбор техники.
Запуск: python3 -I scripts/ai-engineering-code/ch07_finetune_or_rag.py   (только стандартная библиотека)"""
from dataclasses import dataclass


@dataclass
class Case:
    name: str
    failure: str                  # "none", "info", "behavior" или "both"
    has_eval: bool = True         # есть набор для оценки и метрики
    prompt_tuned: bool = True     # prompt проверен системно: ясные инструкции, реальные примеры
    fresh_data: bool = False      # ответы зависят от свежих данных (меняются каждый день)
    labeled_examples: int = 0     # сколько у нас хороших пар (запрос, ответ)
    rare_format: bool = False     # редкий синтаксис, мало примеров в интернете (свой диалект SQL, DSL)
    long_prompt_cost: bool = False  # в каждом prompt десятки примеров: дорого и медленно
    many_tasks: bool = False      # нужно несколько разных задач
    can_host: bool = True         # есть команда, которая сможет хостить и поддерживать модель


def advise(c):
    steps, extras = [], []
    if not c.has_eval:
        steps.append("Сначала eval: критерии и набор запросов (глава 4). Без него не видно, стало ли лучше.")
    if not c.prompt_tuned:
        steps.append("Доработайте prompt: ясные инструкции, примеры из реальных данных, версии prompt (глава 5). "
                     "Часто этого хватает.")
    if c.failure == "none":
        return ["Ошибок нет. Finetuning и RAG не нужны."]
    if c.failure in ("info", "both") or c.fresh_data:
        steps.append("Информационные ошибки или свежие данные: RAG. Начните с поиска по словам (BM25), "
                     "потом embeddings и гибридный поиск (глава 6).")
    if c.failure in ("behavior", "both"):
        method = "LoRA" if c.can_host else "через API провайдера"
        when = "Если после RAG остались ошибки формы или стиля: " if c.failure == "both" else "Поведенческие ошибки: "
        steps.append(f"{when}finetuning ({method}).")
        if c.labeled_examples < 100:
            extras.append(f"Данных мало ({c.labeled_examples} примеров): соберите несколько сотен хороших пар (глава 8).")
        elif c.labeled_examples < 1000:
            extras.append("Сотни примеров: LoRA, полный finetuning вряд ли будет лучше.")
        else:
            extras.append("Тысячи примеров: можно пробовать и LoRA, и полный finetuning, затем сравнить.")
        if c.rare_format:
            extras.append("Редкий синтаксис: finetuning здесь оправдан, готовые модели знают его плохо.")
    if c.long_prompt_cost:
        extras.append("Длинные prompt с примерами: finetuning уберёт примеры из prompt. Проверьте prompt caching, "
                      "он снимает часть выгоды.")
    if c.many_tasks:
        extras.append("Несколько задач: отдельный LoRA-адаптер на задачу (multi-LoRA serving) "
                      "или слияние моделей (model merging).")
    if not c.can_host and c.failure in ("behavior", "both"):
        extras.append("Нет команды для хостинга: выбор моделей и настроек у API ограничен.")
    return [f"{i}. {t}" for i, t in enumerate(steps, 1)] + [f"   + {t}" for t in extras]


CASES = [
    Case("Бот про каталог данных не знает наши таблицы", "info", prompt_tuned=True),
    Case("Text-to-SQL верен, но не в диалекте нашего хранилища", "behavior", labeled_examples=800, rare_format=True),
    Case("Ответы верны, но ломают JSON-схему; prompt писали за 10 минут", "behavior", prompt_tuned=False, labeled_examples=150),
    Case("Нужен стиль отчётов команды, примеров всего 40", "behavior", labeled_examples=40, can_host=False),
    Case("Ответы устарели и стиль чужой", "both", fresh_data=True, labeled_examples=3000),
    Case("30 примеров в каждом prompt: дорого и медленно", "behavior", labeled_examples=2000, long_prompt_cost=True),
    Case("Хотим finetuning, но eval-набора нет", "behavior", has_eval=False, labeled_examples=500),
    Case("Одна модель: рекомендации, изменения заказов, отзывы", "behavior", labeled_examples=1500, many_tasks=True),
    Case("Ошибок не видно, команда просто хочет попробовать finetuning", "none"),
]

for case in CASES:
    print(f"* {case.name}")
    for line in advise(case):
        print("   " + line)
    print()

# Правило «форма или факты» одной строкой: проверка на примерах ошибок
print("== Тип ошибки: форма или факты?")
EXAMPLES = [
    ("Модель назвала 10 студийных альбомов, а их 11", "факты (устарело)", "RAG"),
    ("Спецификация верна, но без деталей, нужных командам", "форма (поведение)", "finetuning"),
    ("HTML от модели не компилируется", "форма (формат)", "finetuning"),
    ("Модель не знает внутренние данные компании", "факты (нет информации)", "RAG"),
]
for text, kind, fix in EXAMPLES:
    print(f"{text:<56} -> {kind:<24} -> {fix}")
