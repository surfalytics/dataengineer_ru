#!/usr/bin/env python3
"""Chapter 5 (analytics frameworks) diagrams. Usage: ch05_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

# Fig 5-5: Lean Analytics stages, gates and how they line up with other frameworks (main diagram)
_st = [("Empathy", "Нашли реальную\nпроблему и решение,\nза которое заплатят",
        "AARRR: Acquisition\nи Activation\nПирамида Эллиса:\nproduct-market fit"),
       ("Stickiness", "Продукт и функции\nудерживают\nпользователей",
        "AARRR: Retention\nДвигатель: sticky\nПирамида Эллиса:\nstack the odds"),
       ("Virality", "Пользователи\nи функции дают рост:\nсвой и платный",
        "AARRR: Referral\nДвигатель: viral\nПирамида Эллиса:\nstack the odds"),
       ("Revenue", "Бизнес-модель\nустойчива, растёт,\nмаржа хорошая",
        "AARRR: Revenue\nДвигатель: paid\nПирамида Эллиса:\nscale growth"),
       ("Scale", "Возможен удачный\nвыход (exit)\nна хороших условиях",
        "Рост за пределами\nLean, внимание\nв масштабе\nПирамида: scale growth")]
_items = [T("Пять этапов Lean Analytics и условия перехода (gates)", 0, -60, 22, "#1971c2")]
_edges = []
for i, (name, gate, mp) in enumerate(_st):
    x = i * 380
    _items += [N(f"s{i}", f"{i + 1}. {name}", x, 0, "g", 280, 80),
               N(f"g{i}", gate, x, 170, "y", 280, 120)]
    _edges.append(E(f"s{i}", f"g{i}", dashed=True))
    if i:
        _edges.append(E(f"s{i - 1}", f"s{i}"))
_items.append(Z("Как этапы совпадают с другими фреймворками", -20, 340, 1840, 240))
for i, (name, gate, mp) in enumerate(_st):
    _items.append(N(f"m{i}", mp, i * 380, 400, "n", 280, 150))
_items.append(T("Жёлтый блок: что должно быть верно, чтобы перейти на следующий этап", 0, 610, 20, "#495057"))
D["ch05-stages-gates"] = dict(items=_items, edges=_edges)

# Fig 5-1: Pirate Metrics AARRR
_aar = [("Acquisition", "q", "Как люди узнают о вас?\nМетрики: трафик, упоминания, цена клика, CAC"),
        ("Activation", "r", "Становится ли случайный посетитель пользователем?\nМетрики: регистрации, пройденный onboarding"),
        ("Retention", "p", "Возвращаются ли люди снова?\nМетрики: вовлечённость, DAU и MAU, churn"),
        ("Revenue", "g", "Зарабатываете ли вы на пользователях?\nМетрики: LTV, конверсия, размер корзины"),
        ("Referral", "y", "Приводят ли пользователи других?\nМетрики: приглашения, viral coefficient")]
_items = [T("Pirate Metrics: пять шагов AARRR", 0, -60, 22, "#1971c2")]
_edges = []
for i, (name, k, q) in enumerate(_aar):
    _items += [N(f"a{i}", name, 0, i * 140, k, 260, 80), T(q, 320, i * 140 + 14, 20, "#343a40")]
    if i:
        _edges.append(E(f"a{i - 1}", f"a{i}"))
_items.append(T("Порядок не строгий: человек может позвать друга раньше, чем заплатит", 0, 710, 20, "#868e96"))
D["ch05-pirate-metrics"] = dict(items=_items, edges=_edges)

# own: three engines of growth (Eric Ries) and the paid engine loop
D["ch05-growth-engines"] = dict(items=[
    T("Три двигателя роста по Эрику Рису", 0, -60, 22, "#1971c2"),
    N("st", "Sticky engine\nлюди возвращаются\nKPI: удержание, churn,\nчастота визитов", 0, 0, "g", 340, 140),
    N("vi", "Viral engine\nпользователи зовут новых\nKPI: viral coefficient,\nviral cycle time", 460, 0, "pu", 340, 140),
    N("pa", "Paid engine\nвыручка идёт в привлечение\nKPI: LTV, CAC,\nсрок окупаемости клиента", 920, 0, "y", 340, 140),
    T("Включают по очереди: слева направо", 0, 170, 20, "#868e96"),
    Z("Цикл paid engine", 700, 230, 800, 340),
    N("c1", "Клиенты платят\n(LTV)", 740, 290, "g", 280, 90),
    N("c2", "Часть выручки\nидёт в привлечение\n(CAC)", 1170, 290, "q", 290, 100),
    N("c3", "Приходят\nновые клиенты", 960, 450, "p", 280, 90),
], edges=[E("st", "vi"), E("vi", "pa"), E("pa", "c1", dashed=True),
          E("c1", "c2"), E("c2", "c3"), E("c3", "c1")])

# Fig 5-2: Sean Ellis's Startup Growth Pyramid
D["ch05-growth-pyramid"] = dict(items=[
    T("Пирамида роста Шона Эллиса: строят снизу вверх", 0, -60, 22, "#1971c2"),
    N("top", "Scale growth\nмасштабный рост", 150, 0, "p", 300, 90),
    N("mid", "Stack the odds\nповысить шансы", 75, 170, "p", 450, 90),
    N("bot", "Product-market fit", 0, 340, "p", 600, 90),
    T("Жмите на газ: новые рынки,\nпродукты и каналы", 680, 15, 20, "#343a40"),
    T("Найдите защищённое преимущество\n(unfair advantage) и настройте его", 680, 185, 20, "#343a40"),
    T("Решите, что и кому продаёте,\nи докажите это", 680, 355, 20, "#343a40"),
    N("test", "Проверка fit: 40% и больше ответят\n«очень расстроюсь», если продукт исчезнет", 0, 500, "y", 600, 90),
], edges=[E("bot", "mid"), E("mid", "top"), E("test", "bot", dashed=True)])

if __name__ == "__main__":
    run_all(D)
