"""Глава 2: preference data и reward model. Из ранга ответов получаем пары, считаем loss Брэдли-Терри,
обучаем крошечную reward model на шумных сравнениях и выбираем лучший из N ответов (best of N).
Ответы описаны тремя числами, «разметчики» — симуляция. Настоящая reward model — это нейросеть, но идея loss та же.
Запуск: python3 -I scripts/ai-engineering-code/ch02_preference.py   (только стандартная библиотека)"""
import math
import random

rng = random.Random(3)
FEATURES = ["полезность", "вежливость", "длина"]
TRUE_W = [2.0, 1.0, -0.5]  # скрытая «настоящая» ценность ответа для пользователя


def utility(f):
    return sum(w * x for w, x in zip(TRUE_W, f))


def new_response():
    return [rng.random() for _ in range(3)]


def sigmoid(x):
    return 1 / (1 + math.exp(-x))


def pairs_from_ranking(ranked):
    return [(ranked[i], ranked[j]) for i in range(len(ranked)) for j in range(i + 1, len(ranked))]


print("== 1. Ранг -> пары (победитель, проигравший)")
print("A > B > C дают:", pairs_from_ranking(["A", "B", "C"]))
print("5 ответов в ранге дают", len(pairs_from_ranking(list("ABCDE"))), "пар =", math.comb(5, 2))

print("\n== 2. Loss Брэдли-Терри для одной пары: -log σ(s_w - s_l)")
for name, sw, sl in [("модель права", 1.2, 0.3), ("баллы равны", 0.5, 0.5), ("модель ошиблась", 0.3, 1.2)]:
    print(f"{name:16s} s_w = {sw}, s_l = {sl}: loss = {-math.log(sigmoid(sw - sl)):.3f}")

print("\n== 3. Баллы 1-7 против сравнений: насколько два шумных разметчика согласны")
NOISE = 0.6


def score_1_7(u):
    return max(1, min(7, round(4 + 1.2 * (u + rng.gauss(0, NOISE)))))


exact = within1 = pair_same = 0
n = 5000
for _ in range(n):
    f = new_response()
    s1, s2 = score_1_7(utility(f)), score_1_7(utility(f))
    exact += s1 == s2
    within1 += abs(s1 - s2) <= 1
    a, b = new_response(), new_response()
    c1 = utility(a) + rng.gauss(0, NOISE) > utility(b) + rng.gauss(0, NOISE)
    c2 = utility(a) + rng.gauss(0, NOISE) > utility(b) + rng.gauss(0, NOISE)
    pair_same += c1 == c2
print(f"оценка 1-7: ровно одинаковые баллы у {exact / n:.0%}, отличаются не больше чем на 1 у {within1 / n:.0%}")
print(f"сравнение двух ответов: одинаковый выбор у {pair_same / n:.0%}  (в книге у разметчиков InstructGPT около 73%)")

print("\n== 4. Обучаем reward model на шумных сравнениях")


def noisy_pair():
    a, b = new_response(), new_response()
    a_wins = utility(a) + rng.gauss(0, NOISE) > utility(b) + rng.gauss(0, NOISE)
    return (a, b) if a_wins else (b, a)  # (победитель, проигравший) по мнению разметчика


train = [noisy_pair() for _ in range(3000)]
test = []
for _ in range(2000):  # тест без шума: победитель — тот, у кого настоящая ценность выше
    a, b = new_response(), new_response()
    test.append((a, b) if utility(a) > utility(b) else (b, a))

w = [0.0, 0.0, 0.0]


def reward(f):
    return sum(x * y for x, y in zip(w, f))


def avg_loss(pairs):
    return sum(-math.log(sigmoid(reward(a) - reward(b))) for a, b in pairs) / len(pairs)


def accuracy(pairs):  # при равных баллах считаем половину успеха
    return sum(1.0 if reward(a) > reward(b) else 0.5 if reward(a) == reward(b) else 0.0 for a, b in pairs) / len(pairs)


for epoch in range(201):
    if epoch in (0, 20, 50, 100, 200):
        print(f"эпоха {epoch:3d}: loss на train = {avg_loss(train):.3f}, точность на чистом тесте = {accuracy(test):.1%}")
    grad = [0.0, 0.0, 0.0]
    for a, b in train:
        g = -(1 - sigmoid(reward(a) - reward(b)))  # производная loss по (s_w - s_l)
        for i in range(3):
            grad[i] += g * (a[i] - b[i]) / len(train)
    w = [wi - 1.5 * gi for wi, gi in zip(w, grad)]

scale = TRUE_W[0] / w[0]
print("признаки:       ", FEATURES)
print("настоящие веса: ", TRUE_W)
print("веса модели:    ", [round(x * scale, 2) for x in w], "(приведены к тому же масштабу)")
labeler = sum(utility(a) > utility(b) for a, b in [noisy_pair() for _ in range(2000)]) / 2000
print(f"один шумный разметчик верно выбирает победителя в {labeler:.0%} случаев, "
      f"а reward model, обученная на таких же шумных метках, на чистом тесте даёт {accuracy(test):.0%}")

print("\n== 5. Best of N: берём N ответов и выбираем лучший по reward model (300 повторов)")
print("   N   настоящая ценность выбранного ответа")
for n_ in (1, 2, 4, 16, 64):
    total = 0.0
    for _ in range(300):
        pool = [new_response() for _ in range(n_)]
        total += utility(max(pool, key=reward))
    print(f"{n_:4d}   {total / 300:6.3f}")
print("потолок: лучший из 64 по настоящей ценности =",
      round(sum(max(utility(new_response()) for _ in range(64)) for _ in range(300)) / 300, 3))
