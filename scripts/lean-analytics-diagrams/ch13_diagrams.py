#!/usr/bin/env python3
"""Chapter 13 (two-sided marketplaces) diagrams. Usage: ch13_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

# Fig 13-1: customer lifecycle of a two-sided marketplace (main diagram)
X1, X2, X3, X4 = 0, 440, 880, 1320
BW = 320
D["ch13-marketplace-lifecycle"] = dict(items=[
    T("Продавцы", X1 + 100, 0, 24, "#f08c00"),
    T("Площадка и сделка", X2 + 60, 0, 24, "#1971c2"),
    T("Покупатели", X3 + 90, 0, 24, "#2f9e44"),
    N("s_visit", "Визиты продавцов", X1, 60, "y", BW, 90),
    N("s_acc", "Аккаунт продавца\nконверсия в регистрацию", X1, 210, "y", BW, 90),
    N("s_list", "Листинги\nвсего и новых в день", X1, 360, "y", BW, 90),
    N("s_fraud", "Жалобы, мошенничество\n% помеченных листингов", X1, 510, "r", BW, 90),
    N("s_rate", "Покупатель\nоценивает продавца", X1, 810, "y", BW, 90),
    N("s_repeat", "Повторный продавец", X1, 960, "y", BW, 90),
    N("s_churn", "Отток продавцов\nLTV продавца", X1, 1110, "r", BW, 90),
    N("c_extra", "Доп. услуги\nвыручка с услуг", X2, 210, "n", BW, 90),
    N("c_results", "Результаты поиска\n% пустых поисков", X2, 360, "p", BW, 90),
    N("c_short", "Шорт-лист\nклики на листинги", X2, 510, "p", BW, 90),
    N("c_trans", "Сделка\nконверсия в покупку", X2, 660, "db", BW, 90),
    N("c_deliv", "Доставка\nдоля довольных сделок", X2, 810, "p", BW, 90),
    N("c_once", "Разовая покупка\nвыручка gross и net", X2, 960, "n", BW, 90),
    N("b_visit", "Визиты покупателей", X3, 60, "g", BW, 90),
    N("b_acc", "Аккаунт покупателя\nконверсия в регистрацию", X3, 210, "g", BW, 90),
    N("b_search", "Поиски\nпоисков на визит", X3, 360, "g", BW, 90),
    N("b_notify", "Уведомления, email\nоткрытия и CTR", X4, 210, "g", BW, 90),
    N("b_rate", "Продавец\nоценивает покупателя", X3, 810, "g", BW, 90),
    N("b_repeat", "Повторный покупатель", X3, 960, "g", BW, 90),
    N("b_churn", "Отток покупателей\nLTV покупателя", X3, 1110, "r", BW, 90),
], edges=[
    E("s_visit", "s_acc"), E("s_acc", "s_list"), E("s_acc", "c_extra"),
    E("s_list", "c_results"), E("s_list", "s_fraud", dashed=True),
    E("b_visit", "b_acc"), E("b_acc", "b_search"), E("b_acc", "b_notify"), E("b_notify", "b_search"),
    E("b_search", "c_results"),
    E("c_results", "c_short"), E("c_short", "c_trans"), E("c_trans", "c_deliv"),
    E("c_deliv", "s_rate"), E("c_deliv", "b_rate"), E("c_deliv", "c_once"),
    E("s_rate", "s_repeat"), E("b_rate", "b_repeat"),
    E("s_repeat", "s_churn", dashed=True), E("b_repeat", "b_churn", dashed=True),
])

# own: chicken-and-egg, seed one side first
D["ch13-chicken-egg"] = dict(items=[
    N("prob", "Курица и яйцо:\nпустой маркетплейс\nникому не нужен", 330, 0, "r", 340, 110),
    N("sup", "Засеять предложение\n(продавцов)", 0, 190, "y", 380, 90),
    N("dem", "Засеять спрос\n(покупателей)", 620, 190, "g", 380, 90),
    N("sup_ex", "Uber платил водителям\n$30 в час.\nDuProprio искал таблички\nи объявления владельцев", 0, 340, "n", 380, 140),
    N("dem_ex", "Amazon сначала продавал\nсвои книги.\nSalesforce сначала\nсделал свою CRM", 620, 340, "n", 380, 140),
    N("sup_m", "Метрики: доход водителя\nна комиссии, время\nподачи машины", 0, 540, "y", 380, 110),
    N("dem_m", "Метрики: удержанные\nпокупатели книг, спрос\nна новые товары", 620, 540, "g", 380, 110),
    N("goal", "Устойчивый маркетплейс:\nобе стороны есть,\nплощадка берёт комиссию", 310, 730, "p", 380, 110),
], edges=[E("prob", "sup"), E("prob", "dem"), E("sup", "sup_ex"), E("dem", "dem_ex"),
          E("sup_ex", "sup_m"), E("dem_ex", "dem_m"), E("sup_m", "goal"), E("dem_m", "goal")])

# own: DuProprio, how the tracked metrics changed
D["ch13-duproprio-stages"] = dict(items=[
    N("d1", "1. Привлечение\nтаблички на газонах,\nчисло листингов", 0, 0, "y", 290, 120),
    N("d2", "2. Здоровье рынка\nвизиты на листинг:\n1000 визитов =\n1 подписка", 350, 0, "p", 290, 120),
    N("d3", "3. Выручка\nдоля проданных,\nсредняя цена пакета", 700, 0, "q", 290, 120),
    N("d4", "4. Оптимизация\nCTR писем, поиск,\nмобильные приложения", 1050, 0, "pu", 290, 120),
    N("top", "Главная метрика сегодня: число продаж\nи доля проданных объектов среди выставленных", 270, 220, "g", 800, 90),
], edges=[E("d1", "d2"), E("d2", "d3"), E("d3", "d4"), E("d3", "top", dashed=True)])

# Table 13-8 as a funnel (May numbers from the book's example)
FW = [760, 660, 560, 460, 420]
FT = ["Все поиски: 55 372 (100%)", "Поиски с результатом: 44 853 (81%)",
      "Клики на листинги: 15 520 (28%)", "Покупки: 931 (1,68%)", "Довольные сделки: 921 (1,66%)"]
FK = ["p", "p", "db", "g", "g"]
D["ch13-conversion-funnel"] = dict(items=[
    T("Воронка маркетплейса за один месяц (пример из книги)", 60, -50, 22, "#1971c2"),
] + [N(f"f{i}", FT[i], (760 - FW[i]) // 2, i * 120, FK[i], FW[i], 70) for i in range(5)],
    edges=[E(f"f{i}", f"f{i + 1}") for i in range(4)])

if __name__ == "__main__":
    run_all(D)
