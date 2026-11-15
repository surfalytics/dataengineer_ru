"""Глава 11: доход спортивного медиасайта из четырёх источников и churn аудитории.
Числа взяты из примера книги. Запуск: python3 -I ch11_media_revenue.py"""

# Инвентарь: сколько страниц видят за месяц
uniques, visits, pages = 20_000, 12, 11
page_views = uniques * visits * pages

sponsor = 4_000                                   # фиксированный контракт
display = page_views * 2 / 1000                   # $2 за 1000 показов (CPM)
ppc = page_views * 2 * 0.008 * 0.37               # 2 объявления, CTR 0,8%, $0,37 за клик
affiliate = page_views * 0.012 * 0.043 * 43.50 * 0.10  # клик, покупка, чек, наша доля

print(f"просмотров страниц: {page_views:,}")
for name, v in [("спонсорство", sponsor), ("display", display), ("клики (PPC)", ppc),
                ("affiliate", affiliate), ("итого", sponsor + display + ppc + affiliate)]:
    print(f"{name:<12} ${v:>10,.2f}")

# Churn аудитории: прирост уникальных минус новые посетители
months = ["Feb", "Mar", "Apr", "May", "Jun", "Jul"]
uniq = [3000, 4000, 5000, 7000, 6000, 7000, 8000]   # с января
new = [1200, 1400, 3000, 1000, 1200, 1100]          # первый визит, с февраля
for m, prev, cur, n in zip(months, uniq, uniq[1:], new):
    print(f"{m}: прирост {cur - prev:>6,}, новых {n:>5,}, ушло {n - (cur - prev):>5,}")
