"""Глава 7: ручки finetuning на игрушечных задачах.
learning rate, число epochs и overfitting, batch size и gradient accumulation, prompt loss weight,
расписание learning rate и оценка токенов для бюджета.
Нужен numpy (см. requirements-ch07.txt).
Запуск: python3 -I scripts/ai-engineering-code/ch07_training_knobs.py"""
import math

import numpy as np

np.set_printoptions(precision=3, suppress=True, linewidth=120)

print("== 1. Learning rate: размер шага. Линейная регрессия, 100 шагов градиентного спуска")
g = np.random.default_rng(0)
X = g.normal(size=(200, 5))
y = X @ np.array([1.0, -2.0, 0.5, 3.0, -1.0]) + g.normal(0, 0.1, 200)


def run_lr(lr, steps=100):
    w, losses = np.zeros(5), []
    for _ in range(steps):
        err = X @ w - y
        losses.append(float(np.mean(err ** 2)))
        w = w - lr * 2 * X.T @ err / len(X)
    return losses


print(f"{'lr':>7} {'шаг 0':>9} {'шаг 10':>10} {'шаг 50':>10} {'шаг 99':>12}  что видно по кривой loss")
for lr in (0.0005, 0.02, 0.4, 1.1):
    L = run_lr(lr)
    if L[-1] > L[0]:
        verdict = "loss растёт: lr слишком велик, модель расходится"
    elif L[-1] > 0.5 * L[0]:
        verdict = "loss стабилен, но почти не падает: lr слишком мал"
    else:
        verdict = "loss падает плавно: lr подходит"
    print(f"{lr:>7} {L[0]:>9.3f} {L[10]:>10.4g} {L[50]:>10.4g} {L[-1]:>12.4g}  {verdict}")

print("\n== 2. Epochs и overfitting: 30 примеров, 40 признаков, из них важны только 5")
g = np.random.default_rng(3)
p, n_train = 40, 30
w_true = np.zeros(p)
w_true[:5] = [2, -1, 1.5, 0.5, -2]
Xt, Xv = g.normal(size=(n_train, p)), g.normal(size=(500, p))
yt = Xt @ w_true + g.normal(0, 1.0, n_train)
yv = Xv @ w_true + g.normal(0, 1.0, 500)
w = np.zeros(p)
history = []
for epoch in range(1, 1001):
    w = w - 0.01 * 2 * Xt.T @ (Xt @ w - yt) / n_train
    history.append((epoch, np.mean((Xt @ w - yt) ** 2), np.mean((Xv @ w - yv) ** 2)))
best = min(history, key=lambda h: h[2])
print(f"{'epoch':>6} {'train loss':>11} {'validation loss':>16}")
for epoch in (1, 10, 30, best[0], 200, 500, 1000):
    h = history[epoch - 1]
    mark = "  <- минимум validation loss" if epoch == best[0] else ""
    print(f"{h[0]:>6} {h[1]:>11.3f} {h[2]:>16.3f}{mark}")
print(f"Train loss падает всё время, validation loss после epoch {best[0]} растёт: это overfitting. Стоп на epoch {best[0]}.")

print("\n== 3. Batch size: шум градиента и gradient accumulation")
g = np.random.default_rng(1)
Xb = g.normal(size=(4096, 5))
yb = Xb @ np.array([1.0, -2.0, 0.5, 3.0, -1.0]) + g.normal(0, 1.0, 4096)
w = np.zeros(5)


def grad(idx):
    return 2 * Xb[idx].T @ (Xb[idx] @ w - yb[idx]) / len(idx)


print(f"{'batch size':>11} {'разброс градиента между батчами':>32}")
for bs in (1, 2, 8, 32, 128):
    gs = np.array([grad(g.choice(4096, bs, replace=False)) for _ in range(300)])
    print(f"{bs:>11} {gs.std(axis=0).mean():>32.3f}")
print("Чем меньше batch, тем сильнее шаги «дёргаются» от выборки к выборке. Это один из простых доводов против batch < 8.")
idx = g.choice(4096, 8, replace=False)
big = grad(idx)
acc = sum(grad(idx[i:i + 2]) for i in range(0, 8, 2)) / 4          # 4 микро-батча по 2 примера
print(f"gradient accumulation: 4 микро-батча по 2 == один батч из 8: {np.allclose(big, acc)}")
print("Память на activations нужна только под микро-батч из 2 примеров, а шаг делается как для батча из 8.")

print("\n== 4. Prompt loss weight: чему учится модель, prompt или ответу")
g = np.random.default_rng(2)
prompt_tokens, response_tokens = 120, 30
prompt_losses = g.gamma(4, 0.5, prompt_tokens)       # средний loss на токенах prompt около 2.0
response_losses = g.gamma(4, 0.25, response_tokens)  # средний loss на токенах ответа около 1.0
print(f"в примере {prompt_tokens} токенов prompt и {response_tokens} токенов ответа")
print(f"{'вес prompt':>11} {'вклад prompt в loss':>20} {'вклад ответа':>13}")
for wp in (1.0, 0.1, 0.0):
    a, b = wp * prompt_losses.sum(), response_losses.sum()
    print(f"{wp:>11.0%} {a / (a + b):>20.0%} {b / (a + b):>13.0%}")
print("При весе 100% почти весь сигнал даёт prompt, хотя на inference его пишет пользователь. 10% это компромисс.")

print("\n== 5. Расписание learning rate: большой шаг в начале, малый в конце (peak lr = 2e-4, 1000 шагов)")
peak, total, warmup = 2e-4, 1000, 50


def lr_at(step, kind):
    if step < warmup:
        return peak * (step + 1) / warmup
    t = (step - warmup) / (total - warmup)
    return peak * (1 - t) if kind == "linear" else peak * 0.5 * (1 + math.cos(math.pi * t))


print(f"{'шаг':>5} {'linear':>10} {'cosine':>10}")
for s in (0, 25, 50, 250, 500, 750, 999):
    print(f"{s:>5} {lr_at(s, 'linear'):>10.2e} {lr_at(s, 'cosine'):>10.2e}")

print("\n== 6. Бюджет: сколько токенов и шагов нужно для finetuning")
print(f"{'примеров':>9} {'токенов в примере':>18} {'epochs':>7} {'micro x accum':>14} {'шагов':>6} {'токенов всего':>14}")
for examples, tokens, epochs, micro, accum in [(500, 300, 8, 4, 4), (5000, 400, 4, 8, 4), (2_000_000, 500, 1, 16, 16)]:
    eff = micro * accum
    steps = math.ceil(examples / eff) * epochs
    print(f"{examples:>9,} {tokens:>18} {epochs:>7} {f'{micro} x {accum} = {eff}':>14} {steps:>6,} {examples * tokens * epochs:>14,}")
