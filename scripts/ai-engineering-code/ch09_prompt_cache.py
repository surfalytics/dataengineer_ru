"""Глава 9: prompt caching (prefix cache). Сколько токенов prefill мы не обрабатываем заново.
Кэш хранит обработанные начала prompt блоками по 16 токенов. Новый prompt берёт из кэша самое длинное совпавшее начало.
Токены здесь случайные числа, настоящая модель не нужна: считаем только, сколько токенов пришлось бы обработать.
Запуск: python3 scripts/ai-engineering-code/ch09_prompt_cache.py   (только стандартная библиотека)"""
import random

BLOCK = 16


class PrefixCache:
    def __init__(self):
        self.root = {}

    def process(self, tokens):
        """Возвращает, сколько токенов надо обработать заново. Потом кладёт prompt в кэш."""
        node, matched = self.root, 0
        blocks = [tuple(tokens[i:i + BLOCK]) for i in range(0, len(tokens) - len(tokens) % BLOCK, BLOCK)]
        for b in blocks:
            if b in node:
                node, matched = node[b], matched + BLOCK
            else:
                break
        node = self.root                      # вставляем все блоки prompt
        for b in blocks:
            node = node.setdefault(b, {})
        return len(tokens) - matched


rng = random.Random(4)
SYSTEM = [rng.randrange(50_000) for _ in range(800)]      # инструкции приложения: одинаковые у всех запросов
EXAMPLES = [rng.randrange(50_000) for _ in range(150)]    # few-shot примеры: тоже одинаковые


def user_part():
    return [rng.randrange(50_000) for _ in range(50)]     # вопрос пользователя: каждый раз новый


print("== 1. Одинаковое начало: система и примеры в начале, вопрос в конце")
N = 200
for title, build in [
    ("стабильная часть в начале", lambda u: SYSTEM + EXAMPLES + u),
    ("переменная часть в начале ", lambda u: u + SYSTEM + EXAMPLES),
]:
    cache, processed, total = PrefixCache(), 0, 0
    for _ in range(N):
        prompt = build(user_part())
        processed += cache.process(prompt)
        total += len(prompt)
    print(f"{title}: обработано {processed:>7} из {total} токенов, пропущено {1 - processed / total:.0%}")
print("Кэш сравнивает начало prompt. Если первым стоит переменный вопрос, совпадения нет, и кэш не помогает.")

print("\n== 2. Длинный диалог: каждый ход добавляет сообщение пользователя и ответ")
cache, system, turns = PrefixCache(), SYSTEM[:500], 10
history, total_no_cache, total_cache = list(system), 0, 0
for turn in range(1, turns + 1):
    history += [rng.randrange(50_000) for _ in range(40)]       # сообщение пользователя
    total_no_cache += len(history)
    total_cache += cache.process(history)
    history += [rng.randrange(50_000) for _ in range(120)]      # ответ модели
print(f"{turns} ходов. Без кэша prefill обработал {total_no_cache} токенов, с кэшем {total_cache}.")
print(f"Экономия {1 - total_cache / total_no_cache:.0%}. Чем длиннее диалог, тем больше пропускаем.")

print("\n== 3. Сколько памяти занимает кэш (как KV cache: растёт с длиной)")
layers, hidden, bytes_per_value = 40, 5120, 2          # Llama 2 13B, FP16, как в блоке про KV cache
per_token = 2 * layers * hidden * bytes_per_value
print(f"один токен в кэше: {per_token / 1e6:.2f} MB; prompt 1000 токенов: {1000 * per_token / 1e9:.2f} GB")
print("Поэтому провайдеры берут плату за хранение кэша и держат его ограниченное время.")
