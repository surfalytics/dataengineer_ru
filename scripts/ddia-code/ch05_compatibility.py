#!/usr/bin/env python3
"""DDIA2, глава 5: совместимость схем.
1) Avro: схема писателя и схема читателя, поля сопоставляются по имени.
2) Старый код теряет новое поле, если не хранит неизвестные поля (рисунок 5-1 книги).
Только стандартная библиотека. Запуск: python3 -I ch05_compatibility.py"""

MISSING = object()

# Версии схемы: список (имя поля, значение по умолчанию). MISSING = default нет.
V1 = [("userName", MISSING), ("favoriteNumber", None)]
V2 = [("userName", MISSING), ("favoriteNumber", None), ("photoUrl", None)]  # новое поле с default


def resolve(record, reader_schema):
    """Переводит запись из схемы писателя в схему читателя, как это делает Avro."""
    out = {}
    for name, default in reader_schema:
        if name in record:
            out[name] = record[name]          # поле есть у обоих
        elif default is not MISSING:
            out[name] = default               # нет у писателя: берём default читателя
        else:
            raise ValueError(f"нет поля {name} и нет default")
    return out                                # поля, которых нет у читателя, пропали


old_row = {"userName": "Martin", "favoriteNumber": 1337}
new_row = {"userName": "Martin", "favoriteNumber": 1337, "photoUrl": "/u/1.jpg"}
print("backward, v2 читает запись v1:", resolve(old_row, V2))
print("forward,  v1 читает запись v2:", resolve(new_row, V1))
try:
    resolve({"favoriteNumber": 7}, V1)
except ValueError as e:
    print("ошибка:", e)

print()


class UserV1:
    """Модель старого кода: знает только два поля."""
    def __init__(self, row, keep_unknown):
        self.userName = row["userName"]
        self.favoriteNumber = row["favoriteNumber"]
        known = {"userName", "favoriteNumber"}
        self.unknown = {k: v for k, v in row.items() if k not in known} if keep_unknown else {}

    def to_row(self):
        return {"userName": self.userName, "favoriteNumber": self.favoriteNumber, **self.unknown}


for keep in (False, True):
    user = UserV1(new_row, keep_unknown=keep)  # старый код читает запись нового кода
    user.favoriteNumber = 42                   # меняет одно поле
    print(f"keep_unknown={keep!s:5} ->", user.to_row())  # и пишет обратно
