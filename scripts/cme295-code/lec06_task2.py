"""Задача 2: порядок частей промпта и стоимость при prompt caching."""
PRICE, CACHED = 10 / 1_000_000, 1 / 1_000_000  # доллары за токен: обычный и из кэша

FIXED = [("tools", 2000), ("rules", 500)]          # одинаковы во всех запросах
VARIABLE = [("context", 50), ("question", 100)]    # меняются в каждом запросе


def cost_per_request(blocks):
    """Кэшируется общий префикс двух запросов подряд: блоки, пока они не меняются."""
    cached = 0
    for name, size in blocks:
        if name in dict(VARIABLE):
            break
        cached += size
    total = sum(size for _, size in blocks)
    return cached, cached * CACHED + (total - cached) * PRICE


bad = VARIABLE + FIXED
good = FIXED + VARIABLE
for title, blocks in (("плохо: переменное сверху", bad), ("хорошо: постоянное сверху", good)):
    cached, cost = cost_per_request(blocks)
    print(f"{title:<28} из кэша: {cached:>4} токенов, 1000 запросов: ${cost * 1000:.2f}")
