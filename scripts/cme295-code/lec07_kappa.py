"""Каппа Коэна: доля совпадений врёт, когда оценщики часто ставят одну и ту же оценку."""
import numpy as np


def kappa(a, b):
    a, b = np.array(a), np.array(b)
    po = np.mean(a == b)                                   # наблюдаемое согласие
    pe = sum(np.mean(a == c) * np.mean(b == c) for c in (0, 1))  # согласие «по случайности»
    return po, pe, (po - pe) / (1 - pe)


def make(both_pass, a_only, b_only, both_fail):
    """1 = pass, 0 = fail. Строим оценки двух оценщиков из таблицы совпадений."""
    alice = [1] * both_pass + [1] * a_only + [0] * b_only + [0] * both_fail
    bob = [1] * both_pass + [0] * a_only + [1] * b_only + [0] * both_fail
    return alice, bob


cases = {
    "оба почти всегда pass": make(85, 5, 5, 5),
    "классы поровну, согласны": make(45, 5, 5, 45),
}
rng = np.random.default_rng(0)
cases["бросают монету"] = (rng.integers(0, 2, 1000), rng.integers(0, 2, 1000))

for name, (a, b) in cases.items():
    po, pe, k = kappa(a, b)
    print(f"{name:26s} po={po:.2f}  pe={pe:.2f}  kappa={k:.2f}")
