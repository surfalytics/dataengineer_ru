"""Задача 3: DPO loss по логарифмам вероятностей."""
import math

beta = 0.1

def sigmoid(x):
    return 1 / (1 + math.exp(-x))

def dpo_loss(lp_w, lp_l, ref_w, ref_l):
    r_w = beta * (lp_w - ref_w)                         # неявное вознаграждение победителя
    r_l = beta * (lp_l - ref_l)                         # и проигравшего
    return -math.log(sigmoid(r_w - r_l))

ref_w, ref_l = -42.0, -38.0                             # ln-вероятности ответов у референсной модели
print("старт (модель = референс):", round(dpo_loss(ref_w, ref_l, ref_w, ref_l), 4))
print("победитель вырос, проигравший упал:", round(dpo_loss(-40.0, -45.0, ref_w, ref_l), 4))
print("всё наоборот:", round(dpo_loss(-45.0, -36.0, ref_w, ref_l), 4))
