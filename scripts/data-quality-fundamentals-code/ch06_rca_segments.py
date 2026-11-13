"""Глава 6, шаг 3 RCA: смотрим на данные по сегментам.
Таблица users: доля null в user_interests выросла. Почему?
Сравниваем две недели в двух сценариях и раскладываем рост по источникам."""
import random

SOURCES = ["twitter", "facebook", "google"]
# обычная доля null по источникам: у twitter она выше всех
BASE_NULL = {"twitter": 0.40, "facebook": 0.10, "google": 0.10}


def make_week(seed, mix, null_rate, n=10_000):
    """mix: доля записей по источникам, null_rate: доля null по источникам"""
    rnd = random.Random(seed)
    rows = []
    for _ in range(n):
        src = rnd.choices(SOURCES, weights=[mix[s] for s in SOURCES])[0]
        is_null = rnd.random() < null_rate[src]
        rows.append((src, is_null))
    return rows


def report(title, rows):
    total_null = sum(1 for _, n in rows if n) / len(rows)
    print(f"{title}: null всего = {total_null:.1%}")
    for s in SOURCES:
        part = [n for src, n in rows if src == s]
        print(f"  {s:<9} доля записей {len(part) / len(rows):5.1%}   null внутри {sum(part) / len(part):5.1%}")


normal_mix = {"twitter": 0.20, "facebook": 0.40, "google": 0.40}
last_week = make_week(1, normal_mix, BASE_NULL)

# сценарий 1: пришло больше пользователей из twitter (например, рекламная кампания)
campaign_mix = {"twitter": 0.45, "facebook": 0.275, "google": 0.275}
week_campaign = make_week(2, campaign_mix, BASE_NULL)

# сценарий 2: источник twitter стал отдавать больше null (ошибка обработки)
broken_null = dict(BASE_NULL, twitter=0.80)
week_broken = make_week(3, normal_mix, broken_null)

report("Прошлая неделя ", last_week)
print()
report("Сценарий 1     ", week_campaign)
print("  -> изменилась доля twitter, null внутри источников прежний: сезон или кампания")
print()
report("Сценарий 2     ", week_broken)
print("  -> доли те же, но null внутри twitter вырос: ошибка в обработке twitter")
