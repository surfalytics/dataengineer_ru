"""Закон Chinchilla на цифрах: сколько токенов нужно модели при заданном бюджете вычислений."""
import math

TOKENS_PER_PARAM = 20          # правило Chinchilla: примерно 20 токенов на параметр


def train_flops(params, tokens):
    # Грубое правило: обучение стоит около 6 FLOPs на параметр на токен
    return 6 * params * tokens


# Два варианта с одним бюджетом: малая модель и большая модель
small_params, small_tokens = 70e9, 1.4e12
budget = train_flops(small_params, small_tokens)
big_params = 280e9
big_tokens = budget / (6 * big_params)

print(f"Бюджет: {budget:.2e} FLOPs")
print(f"Малая: {small_params/1e9:.0f} млрд параметров, {small_tokens/1e12:.2f} трлн токенов,"
      f" токенов на параметр: {small_tokens/small_params:.0f}")
print(f"Большая: {big_params/1e9:.0f} млрд параметров, {big_tokens/1e12:.2f} трлн токенов,"
      f" токенов на параметр: {big_tokens/big_params:.2f}")

# Для любого бюджета C: C = 6 * N * D и D = 20 * N, значит N = sqrt(C / 120)
print()
for c in [1e21, 1e23, 1e25]:
    n = math.sqrt(c / (6 * TOKENS_PER_PARAM))
    d = TOKENS_PER_PARAM * n
    print(f"C = {c:.0e}: параметров {n/1e9:7.1f} млрд, токенов {d/1e12:6.2f} трлн")
