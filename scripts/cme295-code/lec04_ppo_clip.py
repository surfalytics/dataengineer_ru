"""Importance sampling и обрезка (clipping) в PPO на трёх ответах."""
import numpy as np

rng = np.random.default_rng(1)

# Часть 1. Оценить среднее вознаграждение новой политики по ответам старой.
pi_old = np.array([0.5, 0.3, 0.2])
pi_new = np.array([0.6, 0.3, 0.1])
reward = np.array([1.0, 0.0, -1.0])
true_value = (pi_new * reward).sum()

answers = rng.choice(3, size=200000, p=pi_old)                # ответы генерировала СТАРАЯ политика
rho = pi_new[answers] / pi_old[answers]                       # отношение политик (importance sampling ratio)
estimate = (rho * reward[answers]).mean()
naive = reward[answers].mean()                                # без поправки получится среднее старой политики
print(f"точное для новой политики: {true_value:.3f}")
print(f"с поправкой rho:           {estimate:.3f}")
print(f"без поправки:              {naive:.3f}  (это значение старой политики: {(pi_old * reward).sum():.3f})")

# Часть 2. Обрезанная цель PPO: min(rho * A, clip(rho, 1-eps, 1+eps) * A).
eps = 0.2


def ppo_term(rho, A, eps=0.2):
    unclipped = rho * A
    clipped = np.clip(rho, 1 - eps, 1 + eps) * A
    value = min(unclipped, clipped)
    active = unclipped <= clipped                             # градиент есть, только если выбрана ветка без обрезки
    return value, active


print("\nrho   A=+1: цель  градиент | A=-1: цель  градиент")
for r in [0.5, 0.8, 1.0, 1.2, 1.5]:
    vp, ap = ppo_term(r, +1.0)
    vn, an = ppo_term(r, -1.0)
    print(f"{r:.1f}        {vp:5.2f}  {'есть ' if ap else 'нет  '}     |       {vn:5.2f}  {'есть' if an else 'нет'}")
