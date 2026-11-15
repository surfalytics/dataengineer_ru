#!/usr/bin/env python3
"""Chapter 4 (plans, pricing, privacy, accounts) diagrams. Usage: ch04_diagrams.py [name ...]  (no args = all)
The chapter has no figures. All three diagrams are our own."""
from excb import N, E, Z, T, run_all

D = {}

# Own diagram: the plan ladder on two axes - usage headroom and administration
D["ch04-plan-ladder"] = dict(items=[
    Z("Один человек: платите за запас лимитов", -30, -80, 1300, 220),
    N("free", "Free\nбесплатно,\nлёгкие задачи", 0, 0, "n", 250, 110),
    N("pro", "Pro\nрегулярная работа\nкаждый день", 470, 0, "p", 250, 110),
    N("max", "Max\nдолгие сессии на\nфлагманской модели", 940, 0, "pu", 280, 110),
    Z("Организация: платите за администрирование", -30, 250, 1300, 220),
    N("team", "Team\nнебольшая группа:\nобщий счёт и админ", 470, 330, "g", 250, 110),
    N("ent", "Enterprise\nкрупная компания:\nSSO, политики", 940, 330, "y", 280, 110),
], edges=[
    E("free", "pro", "Free мешает\nработе"), E("pro", "max", "Pro мешает\nработе"),
    E("pro", "team", "несколько человек,\nнужен общий счёт"),
    E("team", "ent", "SSO, контроль,\nresidency"),
])

# Own diagram: one question sorts subscription vs API account
D["ch04-subscription-vs-api"] = dict(items=[
    N("q", "Кто обращается\nк Claude?", 370, 0, "q", 300, 100),
    N("h", "Вы сами:\nпишете, думаете,\nанализируете в чате", 0, 230, "p", 340, 120),
    N("s", "Программа:\nприложение, автоматизация,\nагент без человека", 700, 230, "pu", 340, 120),
    N("sub", "Подписка на чат\nPro, Max, Team\nфиксированная цена в месяц", 0, 470, "p", 340, 120),
    N("api", "Аккаунт API\nоплата за токены\n+ лимит расходов", 700, 470, "pu", 340, 120),
    T("Это два разных аккаунта: у них нет общего счёта, лимитов и кредитов.\nЕсть задачи обоих видов? Заведите оба.", 0, 640, 20, "#e03131"),
], edges=[
    E("q", "h", "человек"), E("q", "s", "код"),
    E("h", "sub"), E("s", "api"),
    E("sub", "api", "общего счёта нет", dashed=True, head=False),
])

# Own diagram: how to estimate the monthly API cost before launch
D["ch04-api-cost-estimate"] = dict(items=[
    N("calls", "Сколько вызовов\nв день", 0, 0, "n", 280, 100),
    N("tok", "Сколько токенов\nна вызов:\nвход + выход", 360, 0, "n", 280, 100),
    N("model", "Какая модель:\nHaiku намного\nдешевле Opus", 720, 0, "n", 280, 100),
    N("day", "Стоимость в день\n(цены за токен\nиз документации)", 360, 240, "p", 280, 110),
    N("month", "× 30:\nоценка на месяц", 360, 470, "y", 280, 100),
    N("cap", "Лимит расходов\nдо первой\nстроки кода", 860, 470, "g", 280, 100),
    T("После запуска уточните оценку по реальным данным.", 0, 620, 20, "#495057"),
], edges=[
    E("calls", "day"), E("tok", "day"), E("model", "day"),
    E("day", "month"), E("month", "cap", "задать\nсразу"),
])

if __name__ == "__main__":
    run_all(D)
