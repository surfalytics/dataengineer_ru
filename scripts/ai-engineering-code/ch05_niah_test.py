"""Глава 5: тест «иголка в стоге сена» (needle in a haystack, NIAH) для длинного prompt.
Модель здесь ненастоящая. mock_model() находит иглу с вероятностью, которая зависит от места иглы:
на краях prompt лучше, в середине хуже, а чем длиннее prompt, тем хуже. Эту форму мы задали сами,
по описанию исследования Liu et al. Скрипт показывает устройство теста, а не свойства настоящей модели.
Чтобы измерить свою модель, замените mock_model() вызовом API. Остальной код останется тем же.
Что показывает:
 1. как строится стог: случайные пары «ключ: значение» и одна пара-игла на заданной позиции;
 2. почему иглу надо генерировать самому: случайные идентификаторы нельзя было видеть в обучении;
 3. как считать точность по позициям и как читать результат.
Запуск: python3 -I scripts/ai-engineering-code/ch05_niah_test.py   (только стандартная библиотека)"""
import random
import re


def count_tokens(text):
    return len(re.findall(r"\w+|[^\w\s]+", text))


def make_prompt(n_lines, needle_index, rng):
    """Стог из n_lines пар. На месте needle_index стоит игла. Возвращает prompt, ключ и верное значение."""
    pairs = [(f"k-{rng.getrandbits(32):08x}", f"v-{rng.getrandbits(32):08x}") for _ in range(n_lines)]
    key, value = pairs[needle_index]
    body = "\n".join(f'"{k}": "{v}"' for k, v in pairs)
    prompt = f"Найди значение по указанному ключу в данных ниже.\nДанные:\n{body}\nКлюч: \"{key}\"\nЗначение:"
    return prompt, key, value


def mock_model(prompt, rng):
    """Игрушечная модель. Вероятность найти иглу: 0,95 на краях, 0,55 в середине, ниже для длинных prompts."""
    key = re.search(r'Ключ: "([^"]+)"', prompt).group(1)
    line_start = prompt.index(f'"{key}": ')
    f = line_start / len(prompt)                    # где стоит игла: 0 начало, 1 конец
    n_lines = prompt.count('": "v-')
    p = 0.55 + 0.40 * abs(2 * f - 1) ** 1.5
    p *= 1 - 0.15 * min(1, n_lines / 500)           # длинный стог хуже
    if rng.random() < p:
        return re.search(rf'"{re.escape(key)}": "([^"]+)"', prompt).group(1)
    wrong = re.findall(r'"v-[0-9a-f]+"', prompt)
    return rng.choice(wrong).strip('"')             # модель выдала чужое значение


TRIALS = 300
POSITIONS = [0.0, 0.25, 0.5, 0.75, 1.0]
print("Точность поиска иглы (%), игла стоит на позиции, доля от начала prompt")
for n_lines in (50, 200, 500):
    sample, _, _ = make_prompt(n_lines, 0, random.Random("size"))
    print(f"\nСтог из {n_lines} строк, примерно {count_tokens(sample)} токенов")
    print("позиция | точность |")
    for pos in POSITIONS:
        idx = round(pos * (n_lines - 1))
        ok = 0
        for t in range(TRIALS):
            rng = random.Random(f"{n_lines}-{pos}-{t}")
            prompt, key, value = make_prompt(n_lines, idx, rng)
            ok += mock_model(prompt, rng) == value
        acc = ok / TRIALS
        print(f"{pos:>7.0%} | {acc:7.1%}  | {'#' * round(acc * 40)}")
print("\nЧитаем: на краях точность выше, чем в середине, и она падает с длиной prompt.")
print("Если у вашей модели кривая плоская, длинный контекст вам подходит. Если нет, сокращайте prompt.")
