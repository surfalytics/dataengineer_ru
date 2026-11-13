"""Глава 9: speculative decoding. Draft-модель предлагает K токенов, target-модель проверяет их одним проходом.
Модели здесь игрушечные: следующий токен зависит от двух последних токенов по фиксированному правилу.
Из книги: цикл «предложить K токенов, проверить параллельно, принять самую длинную подходящую часть,
добавить один токен target»; если приняты все K, цикл даёт K + 1 токен, если ни одного, то 1 токен;
пример DeepMind: draft 1,8 мс на токен против 14,1 мс у target (Chinchilla-70B).
Наше добавление: формула среднего числа токенов за цикл и таблица ускорения.
Запуск: python3 scripts/ai-engineering-code/ch09_speculative.py   (только стандартная библиотека)"""
import random

VOCAB = 50


def target_next(context):
    """Игрушечная 'большая' модель: детерминированное правило по двум последним токенам."""
    a, b = context[-2], context[-1]
    return (a * 31 + b * 17 + 7) % VOCAB


def draft_next(context):
    """Игрушечная 'малая' модель: в 80% контекстов совпадает с target, в остальных ошибается."""
    guess = target_next(context)
    h = (context[-1] * 7 + context[-2] * 13) % 10
    return guess if h < 8 else (guess + 1) % VOCAB


def plain_decode(prompt, n):
    seq = list(prompt)
    calls = 0
    for _ in range(n):
        seq.append(target_next(seq))
        calls += 1                       # один вызов большой модели на каждый токен
    return seq, calls


def speculative_decode(prompt, n, k):
    seq = list(prompt)
    target_calls = 0
    accepted_total = 0
    loops = 0
    while len(seq) - len(prompt) < n:
        loops += 1
        draft = []
        for _ in range(k):               # 1. малая модель предлагает K токенов по одному
            draft.append(draft_next(seq + draft))
        target_calls += 1                # 2. большая модель проверяет все K позиций одним параллельным проходом
        j = 0
        while j < k and target_next(seq + draft[:j]) == draft[j]:
            j += 1                       # 3. принимаем самую длинную подходящую часть
        accepted_total += j
        seq += draft[:j]
        seq.append(target_next(seq))     # 4. большая модель добавляет свой токен (при j = k это токен K + 1)
    return seq[:len(prompt) + n], target_calls, accepted_total, loops


print("== 1. Игрушечный пример: результат тот же, вызовов большой модели меньше")
prompt, n, k = [3, 8], 60, 4
plain, plain_calls = plain_decode(prompt, n)
spec, spec_calls, accepted, loops = speculative_decode(prompt, n, k)
print(f"{n} токенов обычным decode: {plain_calls} вызовов target")
print(f"{n} токенов с speculative decoding (K = {k}): {spec_calls} вызовов target")
print(f"тексты одинаковы: {plain == spec}")
print(f"принято токенов draft: {accepted} из {loops * k} предложенных ({accepted / (loops * k):.0%}), токенов за цикл: {n / loops:.2f}")

print("\n== 2. Сколько токенов даёт цикл в среднем")
print("Пусть каждый токен draft принимается с вероятностью a независимо от других. Среднее число токенов за цикл:")
print("(1 - a^(K+1)) / (1 - a). Проверим формулу симуляцией.")
rng = random.Random(1)


def tokens_per_loop_sim(a, k, trials=100_000):
    total = 0
    for _ in range(trials):
        j = 0
        while j < k and rng.random() < a:
            j += 1
        total += j + 1                   # j принятых токенов draft + один токен target
    return total / trials


print(f"{'a':>5}{'K':>4}{'по формуле':>12}{'симуляция':>11}")
for a, k in [(0.5, 4), (0.8, 4), (0.8, 8), (0.9, 4)]:
    print(f"{a:>5}{k:>4}{(1 - a ** (k + 1)) / (1 - a):>12.2f}{tokens_per_loop_sim(a, k):>11.2f}")

print("\n== 3. Ускорение: цена цикла = K шагов draft + один проверочный проход target")
c_draft = 1.8 / 14.1     # draft быстрее в 8 раз: 1,8 мс против 14,1 мс на токен (Chinchilla-70B, DeepMind)
print(f"отношение стоимости шага draft к шагу target = {c_draft:.3f} (примерно 1/8)")
ks = (1, 2, 4, 6, 8, 12)
print(f"{'a':>5}" + "".join(f"{'K=' + str(k):>8}" for k in ks) + "   лучший K")
for a in (0.5, 0.7, 0.8, 0.9):
    row, best = [], (0, 0)
    for k in ks:
        speedup = ((1 - a ** (k + 1)) / (1 - a)) / (k * c_draft + 1)
        row.append(speedup)
        if speedup > best[0]:
            best = (speedup, k)
    print(f"{a:>5}" + "".join(f"{x:>7.2f}x" for x in row) + f"   K = {best[1]}")
print("Чем выше доля принятых токенов, тем больше выигрыш. Слишком большой K не помогает: цепочка принятых токенов обрывается.")

print("\n== 4. Если чип уже загружен вычислениями (MFU высокий), проверка перестаёт быть бесплатной")
a, k = 0.8, 4
for extra in (0.0, 0.1, 0.3, 0.6):
    speedup = ((1 - a ** (k + 1)) / (1 - a)) / (k * c_draft + 1 + extra * k)
    print(f"доплата за проверку: +{extra * k:.1f} шага target -> ускорение {speedup:.2f}x")
print("Speculative decoding работает, потому что decode упирается в память и FLOP/s простаивают. Нет простоя, нет выигрыша.")
