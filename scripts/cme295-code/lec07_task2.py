"""Задача 2: качество LLM-судьи против человека (precision, recall по классу fail и каппа)."""
human = [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]   # 0 = fail, 1 = pass
judge = [0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

tp = sum(h == 0 and j == 0 for h, j in zip(human, judge))   # fail, найденный судьёй
fp = sum(h == 1 and j == 0 for h, j in zip(human, judge))   # судья назвал fail, а человек pass
fn = sum(h == 0 and j == 1 for h, j in zip(human, judge))   # судья пропустил fail
precision, recall = tp / (tp + fp), tp / (tp + fn)
print(f"precision={precision:.2f} recall={recall:.2f}")

n = len(human)
po = sum(h == j for h, j in zip(human, judge)) / n
pe = sum((human.count(c) / n) * (judge.count(c) / n) for c in (0, 1))
print(f"доля совпадений={po:.2f} kappa={(po - pe) / (1 - pe):.2f}")
