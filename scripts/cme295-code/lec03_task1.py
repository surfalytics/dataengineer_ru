"""Задача 1: loss при SFT считаем только по токенам ответа."""
import math

# Вероятность верного токена на каждой позиции: 4 токена запроса и 3 токена ответа
prompt_probs = [0.10, 0.20, 0.05, 0.30]
answer_probs = [0.50, 0.25, 0.80]

def mean_nll(probs):
    return sum(-math.log(p) for p in probs) / len(probs)

sft_loss = mean_nll(answer_probs)                       # учитываем только ответ
naive_loss = mean_nll(prompt_probs + answer_probs)      # так считать нельзя

print("loss по ответу :", round(sft_loss, 4))
print("loss по всему  :", round(naive_loss, 4))
