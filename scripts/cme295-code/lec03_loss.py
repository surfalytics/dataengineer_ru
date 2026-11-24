"""Кросс-энтропия на маленьком примере и bits per byte."""
import math

text = "A teddy bear is reading"
# Вероятность, которую модель дала верному следующему токену на каждой позиции
probs = [0.20, 0.50, 0.60, 0.30, 0.05]          # 5 токенов: A, teddy, bear, is, reading

product = math.prod(probs)                       # вероятность всего текста
nll = [-math.log(p) for p in probs]              # -ln p по каждому токену
loss = sum(nll) / len(probs)                     # кросс-энтропия на токен (в натах)
print("токены  :", len(probs))
print("p(текст):", product)
print("loss    :", round(loss, 4), "нат на токен")

# Почему берут логарифм: произведение быстро уходит в ноль
print("0.3 в степени 1000 :", 0.3 ** 1000)
print("сумма -ln(0.3) x1000:", round(sum(-math.log(0.3) for _ in range(1000)), 1))

# Bits per byte: loss не зависит от токенизатора
total_nats = sum(nll)                            # «удивление» всего текста
n_bytes = len(text.encode("utf-8"))
for name, n_tokens in [("токенизатор A", 5), ("токенизатор B", 10)]:
    per_token = total_nats / n_tokens
    bpb = per_token * n_tokens / n_bytes / math.log(2)
    print(name, "| токенов:", n_tokens, "| loss:", round(per_token, 4), "| BPB:", round(bpb, 4))
