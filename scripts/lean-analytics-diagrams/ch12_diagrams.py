#!/usr/bin/env python3
"""Chapter 12 (user-generated content) diagrams. Usage: ch12_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

# Fig 12-1: engagement funnel with tiers of reddit, Facebook, YouTube
tiers = [
    ("Разовые посетители", "Посетители · посетители · зрители", "n"),
    ("Вернувшиеся посетители", "Lurkers · lurkers · зрители", "n"),
    ("Зарегистрированные", "Redditors · пользователи · аккаунт Google", "p"),
    ("Голосуют и отмечают", "Голос вверх/вниз · лайк, жалоба · палец вверх/вниз", "p"),
    ("Комментаторы", "Ответ · комментарий · комментарий", "g"),
    ("Авторы контента", "Автор поста (OP) · постер · автор видео", "g"),
    ("Модераторы", "Модератор сабреддита · админ группы · —", "y"),
    ("Создатели групп", "Создатель сабреддита · создатель события\nили группы · владелец канала", "y"),
]
items = [T("Воронка вовлечения: чем ниже, тем меньше людей и выше ценность", 0, -90, 22, "#1971c2"),
         T("Примеры: reddit · Facebook · YouTube", 560, -45, 18, "#495057")]
edges = []
for i, (name, ex, k) in enumerate(tiers):
    w = 440 - i * 30
    y = i * 120
    items.append(N(f"t{i}", name, (440 - w) // 2, y, k, w, 80))
    items.append(N(f"e{i}", ex, 560, y, "n", 560, 80))
    edges.append(E(f"t{i}", f"e{i}", dashed=True, head=False))
    if i: edges.append(E(f"t{i-1}", f"t{i}"))
D["ch12-engagement-funnel"] = dict(items=items, edges=edges)

# Fig 12-4: UGC customer lifecycle with metrics at each step
D["ch12-ugc-lifecycle"] = dict(items=[
    T("Жизненный цикл пользователя UGC-сайта и метрики на каждом шаге", 0, -70, 22, "#1971c2"),
    N("share", "Контент, которым\nподелились", 0, 0, "pu", 240, 90),
    N("s1", "Вирусный шеринг\n(CTR, virality)", 340, 0, "q", 250, 90),
    N("s2", "Поиск\n(позиция в выдаче)", 690, 0, "q", 250, 90),
    N("s3", "Платный трафик\n(цена привлечения)", 1040, 0, "q", 250, 90),
    N("vis", "Посетители\n(трафик)", 690, 190, "y", 250, 90),
    N("inv", "Принятые\nприглашения", 200, 190, "pu", 250, 90),
    N("ret", "Вернувшиеся", 690, 360, "p", 250, 80),
    N("sig", "Вошли в аккаунт", 690, 520, "p", 250, 80),
    N("notif", "Уведомления", 200, 520, "pu", 250, 80),
    N("vot", "Голосуют\n(лайк, ретвит, +1)", 690, 680, "p", 250, 90),
    N("com", "Комментируют", 690, 850, "p", 250, 80),
    N("cre", "Создают контент", 690, 1010, "g", 250, 80),
    N("cont", "Контент:\nхороший и плохой", 0, 1010, "g", 240, 90),
    N("reac", "Реактивация", 1180, 360, "g", 220, 80),
    N("dis", "Неактивные", 1180, 1010, "r", 220, 80),
    T("Уйти в неактивные\nможно с любого уровня", 700, 1110, 18, "#495057"),
    N("ab", "Ушли совсем\n(churn rate)", 1180, 1180, "r", 220, 90),
], edges=[
    E("share", "s1"), E("s1", "vis"), E("s2", "vis"), E("s3", "vis"),
    E("vis", "ret"), E("ret", "sig"), E("sig", "vot"), E("vot", "com"), E("com", "cre"),
    E("cre", "cont", "качество, спам"), E("cont", "share", "вирусный контент"),
    E("sig", "inv", dashed=True), E("inv", "vis", "cycle time"),
    E("notif", "sig", "click-through"),
    E("cre", "dis", "давно нет", dashed=True),
    E("dis", "reac", "письма, push"), E("reac", "ret"), E("dis", "ab"),
])

if __name__ == "__main__":
    run_all(D)
