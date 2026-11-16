#!/usr/bin/env python3
"""DDIA, глава 6: номера версий и siblings на одной реплике (пример с корзиной).

Сервер хранит для ключа номер версии и все значения, которые ещё не перезаписаны.
Клиент пишет с номером версии из прошлого чтения. Сервер удаляет значения
с этой версией и ниже, а более новые оставляет: они параллельны новой записи.
"""


class Server:
    def __init__(self):
        self.version = 0
        self.siblings = {}  # версия -> значение

    def write(self, value, based_on):
        # значения с версией <= based_on клиент уже видел и слил в value
        self.siblings = {v: val for v, val in self.siblings.items() if v > based_on}
        self.version += 1
        self.siblings[self.version] = value
        return dict(self.siblings), self.version


def merge(siblings, item):
    """Клиент сливает siblings (объединение без повторов) и добавляет свой товар."""
    items = [x for v in sorted(siblings) for x in siblings[v]]
    return list(dict.fromkeys(items + [item]))


def show(step, who, sent, based_on, siblings):
    vals = "; ".join(f"v{v}: {', '.join(val)}" for v, val in sorted(siblings.items()))
    print(f"{step}. {who} пишет [{', '.join(sent)}] на основе v{based_on} -> {vals}")


server = Server()
seen1, ver1 = {}, 0  # что клиент 1 знает о ключе
seen2, ver2 = {}, 0  # что клиент 2 знает о ключе

steps = [(1, "молоко"), (2, "яйца"), (1, "мука"), (2, "ветчина"), (1, "бекон")]
for n, (client, item) in enumerate(steps, 1):
    seen, ver = (seen1, ver1) if client == 1 else (seen2, ver2)
    value = merge(seen, item)
    siblings, new_ver = server.write(value, ver)
    show(n, f"клиент {client}", value, ver, siblings)
    if client == 1:
        seen1, ver1 = siblings, new_ver
    else:
        seen2, ver2 = siblings, new_ver
