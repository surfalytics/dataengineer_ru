"""Position bias у LLM-судьи: имитация судьи и проверка с обменом местами."""
import numpy as np

rng = np.random.default_rng(7)
N = 2000
gap = rng.uniform(0.1, 1.0, N)          # насколько лучший ответ лучше худшего
BIAS = 0.4                              # судья «любит» ответ на первом месте


def judge(first_better, gap, rng):
    """True, если судья выбрал ответ на первом месте."""
    sign = 1 if first_better else -1
    score = sign * gap + BIAS + rng.normal(0, 0.3, len(gap))
    return score > 0


# 1) Лучший ответ всегда стоит первым, потом всегда вторым
acc_first = judge(True, gap, rng).mean()
acc_second = 1 - judge(False, gap, rng).mean()
print(f"лучший на первом месте: верно {acc_first:.2f}")
print(f"лучший на втором месте: верно {acc_second:.2f}")

# 2) Спрашиваем дважды: (A, B) и (B, A). Лучший ответ — это A.
v1 = judge(True, gap, rng)              # A на первом месте: судья выбирает A, если True
v2 = ~judge(False, gap, rng)            # B первым, A вторым: судья выбирает A, если выбрал не первый
agree = v1 == v2
print(f"вердикт сменился после обмена: {1 - agree.mean():.2f}")
print(f"верно среди стабильных пар: {v1[agree].mean():.2f}  (доля стабильных {agree.mean():.2f})")
