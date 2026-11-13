"""Глава 10: ограничения user feedback. Три симуляции, только стандартная библиотека.

1) Position bias: на первую позицию кликают чаще. Если лучший вариант всегда стоит вторым,
   по сырым кликам он проигрывает. Помогают случайный порядок или поправка на позицию.
2) Degenerate feedback loop: система показывает то, что набрало больше кликов. Начальная случайность
   закрепляется. Небольшая доля случайного показа (exploration) лечит это.
3) «Кошачий рай»: небольшой перекос в feedback раскручивает перекос в продукте.
Числа придуманы для примера. Запуск: python3 -I scripts/ai-engineering-code/ch10_feedback_loop.py
"""
import random

EXAM = {1: 1.0, 2: 0.55}    # шанс, что пользователь вообще посмотрит на позицию

# --- 1. Position bias ----------------------------------------------------------
QUALITY = {"A": 0.30, "B": 0.40}   # настоящая вероятность клика, если пользователь посмотрел. B лучше
N = 20000


def clicks(order, rng):
    """Показываем два варианта в порядке order. Возвращаем клики по каждому."""
    out = {"A": 0, "B": 0}
    for _ in range(N):
        for pos, item in enumerate(order, start=1):
            if rng.random() < EXAM[pos] * QUALITY[item]:
                out[item] += 1
    return out


print("== 1. Position bias: A всегда первый, B (лучший) всегда второй")
rng = random.Random(1)
c = clicks(("A", "B"), rng)
print(f"сырые клики на {N} показов: A = {c['A']}, B = {c['B']}  -> по кликам «лучше A»")
print(f"поправка на позицию (клики / шанс просмотра): A = {c['A'] / EXAM[1] / N:.3f}, B = {c['B'] / EXAM[2] / N:.3f}  -> «лучше B»")
c1, c2 = clicks(("A", "B"), rng), clicks(("B", "A"), rng)
print(f"случайный порядок (половина показов так, половина иначе): A = {c1['A'] + c2['A']}, B = {c1['B'] + c2['B']}  -> «лучше B»")

# --- 2. Degenerate feedback loop ----------------------------------------------
TRUE = [0.50, 0.52, 0.55, 0.48, 0.58]     # настоящее качество пяти видео. Лучшее: номер 4
ROUNDS, USERS = 300, 20


def simulate(seed, explore):
    rng = random.Random(seed)
    shown = [1] * len(TRUE)               # старт: у каждого один показ и один клик
    clicked = [1] * len(TRUE)
    best_shown = 0
    for _ in range(ROUNDS):
        top = max(range(len(TRUE)), key=lambda i: clicked[i] / shown[i])
        pick = rng.randrange(len(TRUE)) if rng.random() < explore else top
        k = sum(rng.random() < TRUE[pick] for _ in range(USERS))
        shown[pick] += USERS
        clicked[pick] += k
        best_shown += pick == 4
    leader = max(range(len(TRUE)), key=lambda i: clicked[i] / shown[i])
    return leader == 4, best_shown / ROUNDS


print("\n== 2. Degenerate feedback loop: 5 видео, лучшее имеет качество 0,58, 200 запусков")
for name, explore in [("всегда показываем лидера", 0.0), ("10% случайных показов", 0.10), ("30% случайных показов", 0.30)]:
    res = [simulate(seed, explore) for seed in range(200)]
    found = sum(r[0] for r in res) / len(res)
    share = sum(r[1] for r in res) / len(res)
    print(f"{name:26s}: лучшее видео стало лидером в {found:5.1%} запусков, его доля показов {share:5.1%}")

# --- 3. «Кошачий рай» -----------------------------------------------------------
# Придуманная динамика. В мире 10% любителей кошек. Если продукт показывает кошек, любители кошек приходят
# чаще (сарафанное радио). Остальные уходят, когда не видят своего. Система учится на feedback тех, кто остался.
print("\n== 3. «Кошачий рай»: доля кошек в генерации, раунд за раундом")
cat_share = 0.10
history = [cat_share]
for _ in range(14):
    cat_users = 10 * (1 + 20 * cat_share)
    other_users = 90 * (1 - cat_share)
    feedback_cat = cat_users / (cat_users + other_users)      # доля feedback «кошки — это хорошо»
    cat_share = 0.5 * cat_share + 0.5 * feedback_cat          # система сдвигается к feedback
    history.append(cat_share)
print("доля кошек по раундам:", " -> ".join(f"{h:.0%}" for h in history[::2]))
print(f"любителей кошек среди активных пользователей в конце: {feedback_cat:.0%}, в мире их 10%")
