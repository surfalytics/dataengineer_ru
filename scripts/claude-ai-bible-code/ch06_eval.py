"""Глава 6: маленький eval для prompt, который сортирует письма на lead, support и spam.
Вместо модели здесь две простые функции: «старая» и «новая» версия prompt.
Идея та же: один тестовый набор, счёт до и после правки."""

TEST_SET = [  # (письмо, правильная метка)
    ("Хотим купить 50 лицензий, пришлите цену", "lead"),
    ("Не могу войти в аккаунт после сброса пароля", "support"),
    ("Вы выиграли миллион, перейдите по ссылке", "spam"),
    ("Сколько стоит тариф для команды из 10 человек?", "lead"),
    ("Отчёт не грузится второй день", "support"),
    ("Дешёвые часы, скидка 90%, только сегодня", "spam"),
    ("Можно ли договориться о демо на следующей неделе?", "lead"),
    ("Ошибка 500 при экспорте в CSV", "support"),
    ("Срочно подтвердите данные карты по ссылке", "spam"),
    ("Нужен счёт на оплату годовой подписки", "lead"),
    ("Как поменять email в профиле?", "support"),
    ("Проблема с оплатой: деньги списали дважды", "support"),
]


def prompt_v1(text: str) -> str:
    t = text.lower()
    if "ссылк" in t or "скидка" in t:
        return "spam"
    if "цен" in t or "стоит" in t or "оплат" in t:
        return "lead"
    return "support"


def prompt_v2(text: str) -> str:  # правка: жалоба на оплату — это support, а не lead
    t = text.lower()
    if "ссылк" in t or "скидка" in t:
        return "spam"
    if "проблем" in t or "ошибк" in t or "списали" in t:
        return "support"
    if "цен" in t or "стоит" in t or "оплат" in t or "купить" in t or "демо" in t:
        return "lead"
    return "support"


for name, fn in [("v1", prompt_v1), ("v2", prompt_v2)]:
    misses = [(i, exp, fn(txt)) for i, (txt, exp) in enumerate(TEST_SET, 1) if fn(txt) != exp]
    print(f"{name}: {len(TEST_SET) - len(misses)} из {len(TEST_SET)}")
    for i, exp, got in misses:
        print(f"  письмо {i}: ждали {exp}, получили {got}")
