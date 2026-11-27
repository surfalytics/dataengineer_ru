---
title: "Когда метод не должен возвращать self"
prev: {"label":"Когда возвращают self","link":"/interview/questions/python/classes/return-self/"}
next: {"label":"Контекстный менеджер","link":"/interview/questions/python/classes/context-managers/"}
editUrl: false
---

Когда метод не должен возвращать `self`?

## Ответ

Метод не должен возвращать `self`, если по контракту он **не изменяет исходный объект, а создаёт изменённую копию**. В таком случае нужно вернуть новый объект. Иначе вызывающий код будет считать, что получил независимый результат, но продолжит работать со старым экземпляром.

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Point:
    x: int
    y: int

    def moved(self, dx: int, dy: int) -> "Point":
        return Point(self.x + dx, self.y + dy)


original = Point(1, 2)
moved = original.moved(10, 20)

print(original)  # Point(x=1, y=2)
print(moved)     # Point(x=11, y=22)
```

## Метод изменяет объект на месте

Для методов, изменяющих объект на месте, распространённая конвенция Python — вернуть `None`. Это явно показывает мутацию и не создаёт впечатление, что получен новый объект.

```python
class Counter:
    def __init__(self):
        self.value = 0

    def increment(self) -> None:
        self.value += 1


counter = Counter()
result = counter.increment()

print(counter.value)  # 1
print(result)         # None
```

Так работают, например, `list.append()` и `list.sort()`.

## Когда возвращать `self` допустимо

Возврат `self` оправдан в явно спроектированном fluent или builder API, где цепочки вызовов являются частью контракта:

```python
class QueryBuilder:
    def __init__(self):
        self.parts = []

    def select(self, value):
        self.parts.append(f"SELECT {value}")
        return self

    def from_table(self, table):
        self.parts.append(f"FROM {table}")
        return self


query = QueryBuilder().select("name").from_table("users")
```

Главное — не смешивать контракты:

- функциональное преобразование возвращает новый объект;
- обычная in-place-мутация часто возвращает `None`;
- `self` возвращают только для явно заявленного chaining API.

В pandas операции по умолчанию обычно возвращают новый объект. Варианты с `inplace=True` часто избегают: они усложняют композицию и не всегда дают ожидаемую экономию памяти.
