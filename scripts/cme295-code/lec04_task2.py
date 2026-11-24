"""Задача 2: один член цели PPO с обрезкой."""


def ppo_term(rho, A, eps=0.2):
    lo, hi = 1 - eps, 1 + eps
    clipped_rho = min(max(rho, lo), hi)
    return min(rho * A, clipped_rho * A)


for rho, A in [(1.0, 2.0), (1.5, 2.0), (0.5, 2.0), (1.5, -2.0), (0.5, -2.0)]:
    print(f"rho={rho}, A={A:+}: {ppo_term(rho, A):+.2f}")
