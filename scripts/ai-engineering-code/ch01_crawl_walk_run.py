"""Глава 1: Crawl-Walk-Run на примере бота поддержки.
Идея книги: сначала AI только подсказывает оператору (crawl). Если операторы почти всегда берут подсказку без правок,
для этого типа вопросов AI отвечает сам (walk/run). Здесь это моделируется на сгенерированных обращениях.
Что считаем: acceptance rate по типам вопросов, ворота «>= 95%», итоговую долю автоматизации и цель бизнеса.
Все вероятности придуманы. В реальной системе acceptance берут из логов оператора, а подсказки даёт настоящая модель.
Запуск: python3 -I scripts/ai-engineering-code/ch01_crawl_walk_run.py   (только стандартная библиотека)"""
import random

GATE = 0.95        # порог: доля подсказок, принятых без правок
MIN_SAMPLES = 200  # минимум проверенных подсказок на тип вопроса
TARGET = 0.60      # цель бизнеса: автоматизировать 60% обращений
TRAFFIC = {"simple": 0.45, "medium": 0.35, "hard": 0.20}  # доли типов вопросов в потоке


def review_drafts(rng, accept_prob, n_requests):
    """Crawl: AI пишет подсказку, оператор решает, взять её как есть или переписать."""
    stats = {k: [0, 0] for k in TRAFFIC}  # тип -> [принято без правок, всего]
    kinds = rng.choices(list(TRAFFIC), weights=list(TRAFFIC.values()), k=n_requests)
    for kind in kinds:
        stats[kind][1] += 1
        if rng.random() < accept_prob[kind]:
            stats[kind][0] += 1
    return stats


def report(title, stats):
    print(f"-- {title}")
    promoted = []
    for kind, (ok, total) in stats.items():
        rate = ok / total
        passed = rate >= GATE and total >= MIN_SAMPLES
        if passed:
            promoted.append(kind)
        print(f"   {kind:<7} проверено {total:>4}, принято без правок {rate:6.1%}, ворота: {'ДА' if passed else 'нет'}")
    automation = sum(TRAFFIC[k] for k in promoted)
    verdict = "цель достигнута" if automation >= TARGET else "до цели не хватает"
    print(f"   AI отвечает сам на: {promoted or 'ничего'}; автоматизировано {automation:.0%} обращений ({verdict}, цель {TARGET:.0%})")
    return automation


rng = random.Random(11)
print("== 1. Crawl: первая версия бота (подсказки операторам)")
v1 = {"simple": 0.97, "medium": 0.72, "hard": 0.30}
report("версия 1, 2000 обращений", review_drafts(rng, v1, 2000))

print("\n== 2. Улучшили prompt и контекст: средние вопросы стали лучше")
v2 = {"simple": 0.97, "medium": 0.96, "hard": 0.35}
report("версия 2, 2000 обращений", review_drafts(rng, v2, 2000))

print("\n== 3. Почему нужен минимум проверок: малая выборка даёт ложный «зелёный свет»")
true_rate = 0.93  # на самом деле бот ниже порога
for n in [20, 100, 500]:
    trials = 2000
    false_green = 0
    for _ in range(trials):
        ok = sum(rng.random() < true_rate for _ in range(n))
        if ok / n >= GATE:
            false_green += 1
    print(f"   проверено {n:>3} подсказок: ложно прошли ворота в {false_green / trials:5.1%} случаев (настоящий уровень {true_rate:.0%})")
