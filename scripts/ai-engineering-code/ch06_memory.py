"""Глава 6: memory системы: short-term (контекст) и long-term (внешнее хранилище), стратегии управления.
Показывает: бюджет контекста (часть отдана под long-term), переполнение и стратегию FIFO,
риск FIFO (теряется цель разговора), memory retrieval из long-term, сжатие в summary и обработку
противоречий (новый факт заменяет старый). Токены здесь = слова; summarize() — простое правило
(в реальной системе это вызов модели).
Запуск: python3 -I scripts/ai-engineering-code/ch06_memory.py   (только стандартная библиотека)"""
import re

CONTEXT_LIMIT = 90   # «токенов» в контексте
RESERVED = 0.30      # доля контекста под информацию из long-term
SHORT_CAP = int(CONTEXT_LIMIT * (1 - RESERVED))
print(f"== 0. Бюджет: контекст {CONTEXT_LIMIT} токенов, под long-term отдано {RESERVED:.0%}, на short-term остаётся {SHORT_CAP}")

dialog = [
    "I am planning a two-week trip to Vietnam with a budget of 5000 dollars and I am vegetarian.",
    "Which city should I visit first?",
    "Hanoi is a good start because the old quarter is easy to walk.",
    "How many days do I need there?",
    "Three days are enough for the main sights.",
    "What about transport between cities?",
    "Night trains are cheap and flights are fast.",
    "Is it safe to take taxis?",
    "Use a ride app and check the price before the ride.",
    "What should I pack?",
    "Light clothes and a rain jacket for the wet season.",
]


def tokens(text):
    return len(text.split())


class Memory:
    def __init__(self, strategy):
        self.strategy, self.short, self.long = strategy, [], []

    def used(self):
        return sum(tokens(m) for m in self.short)

    def add(self, message):
        self.short.append(message)
        while self.used() > SHORT_CAP and len(self.short) > 1:
            oldest = self.short.pop(0)  # FIFO: что вошло первым, уходит первым
            if self.strategy == "fifo_drop":
                continue                # просто забываем
            if self.strategy == "fifo_to_longterm":
                self.long.append(oldest)  # переносим в long-term
            elif self.strategy == "summary":
                self.long.append(summarize(oldest))  # в long-term кладём сжатую версию

    def retrieve(self, query, k=1):
        """memory retrieval: ищем в long-term по пересечению слов (как простейший term-based поиск)."""
        q = set(re.findall(r"[a-z0-9]+", query.lower()))
        scored = sorted(self.long, key=lambda m: -len(q & set(re.findall(r"[a-z0-9]+", m.lower()))))
        return [m for m in scored[:k] if q & set(re.findall(r"[a-z0-9]+", m.lower()))]


def summarize(text):
    """MOCK: оставляем числа и слова с большой буквы (сущности). Модель сделала бы связный пересказ."""
    keep = [w for w in re.findall(r"[A-Za-z0-9]+", text) if w[0].isdigit() or (w[0].isupper() and w != "I") or w in ("budget", "vegetarian", "trip")]
    return "summary: " + " ".join(keep)


print("\n== 1. Три стратегии на одном диалоге; потом спрашиваем: «What is my budget?»")
for strategy in ("fifo_drop", "fifo_to_longterm", "summary"):
    mem = Memory(strategy)
    for msg in dialog:
        mem.add(msg)
    in_short = any("5000" in m for m in mem.short)
    found = mem.retrieve("What is my budget for the trip?", k=1)
    print(f"[{strategy}] short-term занято {mem.used()} из {SHORT_CAP}, сообщений: {len(mem.short)}; в short-term есть бюджет: {in_short}")
    if strategy == "fifo_drop":
        print("  long-term нет. Бюджет потерян: модель переспросит или выдумает.")
    else:
        print(f"  из long-term найдено: {found}")
print("Самое первое сообщение содержало цель разговора, и FIFO убрал его первым.")

print("\n== 2. Что остаётся в short-term после FIFO")
mem = Memory("fifo_to_longterm")
for msg in dialog:
    mem.add(msg)
for m in mem.short:
    print("  short:", m[:60])
print(f"в long-term перенесено сообщений: {len(mem.long)}")

print("\n== 3. Противоречия: новый факт заменяет старый (merge / replace / add)")
facts = {}


def remember(key, value, turn):
    if key not in facts:
        facts[key] = (value, turn)
        return f"добавили {key}={value}"
    old_value, old_turn = facts[key]
    if old_value == value:
        return f"{key}={value} уже есть, повтор"
    facts[key] = (value, turn)  # правило: побеждает более новое. Можно спросить модель или пользователя.
    return f"заменили {key}: {old_value} (ход {old_turn}) -> {value} (ход {turn})"


for turn, (k, v) in enumerate([("budget", "5000"), ("diet", "vegetarian"), ("budget", "5000"), ("budget", "7000")], 1):
    print(f"ход {turn}: {remember(k, v, turn)}")
print("итоговая память:", {k: v for k, (v, _) in facts.items()})
print("Правило «новое побеждает» — одно из возможных. Иногда противоречие нужно показать пользователю.")
