"""Глава 4: data contamination. Ищем пересечение benchmark с training data по n-gram (как описано в книге),
делим benchmark на «грязные» и «чистые» примеры и сравниваем score на всех примерах и только на чистых.
Данные искусственные: часть вопросов benchmark нарочно подмешана в training corpus.
«Модель» тоже симулируется: запомненные вопросы она решает почти всегда, остальные хуже.
Запуск: python3 scripts/ai-engineering-code/ch04_contamination.py   (только стандартная библиотека)"""
import random

rng = random.Random(5)
SUBJECT = ["таблица", "очередь", "индекс", "кэш", "партиция", "шард", "поток", "задача", "витрина", "реплика"]
ACTION = ["обновляется", "блокируется", "пересчитывается", "копируется", "сжимается", "читается", "очищается"]
WHEN = ["при ночной загрузке", "во время пиковой нагрузки", "после смены схемы", "при откате релиза",
        "в момент деплоя", "при сбое диска", "после пересчёта статистики"]
TAIL = ["для отчётов финансового отдела", "в основном кластере", "на тестовом стенде", "в облачном хранилище",
        "в потоковом контуре", "для внутренних сервисов"]


def sentence():
    return (f"{rng.choice(SUBJECT)} {rng.choice(ACTION)} {rng.choice(WHEN)} job-{rng.randint(1000, 9999)} "
            f"{rng.choice(TAIL)} при нагрузке {rng.randint(10, 999)} запросов")


# benchmark: 100 вопросов; training corpus: 300 документов
NQ = 100
benchmark = [f"Вопрос {i}: как ведёт себя {sentence()} в системе {rng.choice(SUBJECT)}-{i}?" for i in range(NQ)]
leaked_ids = set(rng.sample(range(NQ), 45))     # 45 вопросов утекли в training data
corpus = []
for _ in range(300):
    corpus.append(" ".join(sentence() for _ in range(rng.randint(3, 6))))
for i in leaked_ids:                            # вопрос внутри обычного документа
    corpus.append(sentence() + " " + benchmark[i] + " " + sentence())


def ngrams(text, n):
    w = text.lower().replace("?", "").replace(":", "").split()
    return {tuple(w[i:i + n]) for i in range(len(w) - n + 1)}


def dirty_ids(n):
    index = set()
    for doc in corpus:
        index |= ngrams(doc, n)
    return {i for i, q in enumerate(benchmark) if ngrams(q, n) & index}


print("== 1. Сколько вопросов объявлено «грязными» при разной длине n-gram (настоящих утечек 45)")
for n in (2, 4, 8, 13):
    found = dirty_ids(n)
    print(f"n={n:2d}: грязных {len(found):2d}, из них настоящих {len(found & leaked_ids):2d}, ложных {len(found - leaked_ids):2d}")

N_GRAM = 13  # как в книге: 13 токенов подряд
dirty = dirty_ids(N_GRAM)
clean = set(range(NQ)) - dirty

# симуляция «модели»: запомненное решает с вероятностью 0.97, незнакомое с вероятностью 0.62
correct = {i: rng.random() < (0.97 if i in leaked_ids else 0.62) for i in range(NQ)}


def score(ids):
    ids = list(ids)
    return sum(correct[i] for i in ids) / len(ids)


all_s, dirty_s, clean_s = score(range(NQ)), score(dirty), score(clean)
print(f"\n== 2. Score при n={N_GRAM}")
print(f"всего примеров: {NQ}, грязных: {len(dirty)} ({len(dirty) / NQ:.0%}), чистых: {len(clean)} ({len(clean) / NQ:.0%})")
print(f"score на всех примерах: {all_s:.3f}")
print(f"score на грязных:       {dirty_s:.3f}")
print(f"score на чистых:        {clean_s:.3f}")
print(f"относительная разница (чистые против всех): {(clean_s - all_s) / all_s:+.1%}")
print("Честный отчёт: доля чистых примеров, score на всех и score на чистых. Три числа, а не одно.")
