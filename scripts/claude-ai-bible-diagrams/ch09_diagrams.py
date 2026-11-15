#!/usr/bin/env python3
"""Chapter 9 (the apps: web, desktop, mobile, voice) diagrams. Usage: ch09_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

# main (own): one brain, several doors
doors = [
    ("web", "Web: claude.ai\nновое приходит первым"),
    ("desk", "Desktop: Mac, Windows\nglobal hotkey, файлы"),
    ("mob", "Телефон: iOS, Android\nкамера, уведомления"),
    ("voice", "Голосовой режим\nкогда руки заняты"),
]
items = [N(k, t, i * 340, 0, "p", 300, 110) for i, (k, t) in enumerate(doors)]
items += [
    N("acc", "Ваш аккаунт на серверах Anthropic:\nразговоры, проекты, настройки", 170, 280, "y", 1000, 110),
    N("opus", "Opus 4.8\nсложные задачи", 170, 540, "g", 300, 100),
    N("sonnet", "Sonnet 4.6\nвыбор по умолчанию", 520, 540, "g", 300, 100),
    N("haiku", "Haiku 4.5\nбыстрые ответы", 870, 540, "g", 300, 100),
    T("Приложения = доступ", 1390, 40, 22, "#1971c2"),
    T("Модели = возможности", 1390, 570, 22, "#2f9e44"),
]
edges = [E(k, "acc") for k, _ in doors] + [E("acc", m) for m in ("opus", "sonnet", "haiku")]
D["ch09-one-brain-doors"] = dict(items=items, edges=edges)

# own: what syncs between devices and what stays on one device
D["ch09-sync-split"] = dict(items=[
    N("acc", "Аккаунт на сервере:\nистория разговоров, проекты,\nнастройки аккаунта", 300, 0, "y", 560, 130),
    N("web", "Браузер", 0, 280, "p", 300, 90),
    N("desk", "Desktop", 430, 280, "p", 300, 90),
    N("mob", "Телефон", 860, 280, "p", 300, 90),
    N("dl", "Остаётся на компьютере:\nglobal hotkey,\nлокальные файлы", 430, 480, "r", 300, 130),
    N("ml", "Остаётся на телефоне:\nнастройки приложения\nи уведомлений", 860, 480, "r", 300, 130),
    N("cloud", "Нужен файл везде?\nПоложите его в облачный\nдиск и подключите", 0, 480, "g", 300, 130),
], edges=[E("acc", "web"), E("acc", "desk"), E("acc", "mob"),
          E("desk", "dl", dashed=True), E("mob", "ml", dashed=True)])

# own: match the surface to the task (merges the voice section and the setup section)
rows = [
    ("Длинный текст, сравнение,\nпроекты", "Браузер или desktop", "p"),
    ("Быстрый вопрос,\nне уходя из работы", "Desktop: global hotkey", "p"),
    ("Фото, документ, вывеска,\nруки или глаза заняты", "Телефон: камера и голос", "pu"),
    ("Код, точные цифры, имена,\nтекст для копирования", "Печатать и читать,\nне голос", "q"),
    ("Попробовать новую\nфункцию", "Браузер: claude.ai", "p"),
]
items, edges = [T("Задача", 120, -50, 22, "#495057"), T("Поверхность", 720, -50, 22, "#495057")], []
for i, (task, surf, k) in enumerate(rows):
    y = i * 140
    items += [N(f"t{i}", task, 0, y, "n", 400, 100), N(f"s{i}", surf, 620, y, k, 380, 100)]
    edges.append(E(f"t{i}", f"s{i}"))
D["ch09-surface-choice"] = dict(items=items, edges=edges)

if __name__ == "__main__":
    run_all(D)
