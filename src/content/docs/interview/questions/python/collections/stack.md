---
title: "Стек (stack) в Python"
prev: {"label":"Кортеж и хешируемость","link":"/interview/questions/python/collections/tuple/"}
next: {"label":"Параметры и аргументы","link":"/interview/questions/python/functions/arguments/"}
editUrl: false
---

Что такое стек?

## Ответ

**Стек** (`stack`) — структура данных, работающая по принципу **LIFO** (`Last In, First Out`): последний добавленный элемент извлекается первым.

Основные операции:

| Операция | Назначение | Сложность |
| --- | --- | --- |
| `push` | добавить элемент на вершину | `O(1)` |
| `pop` | удалить и вернуть верхний элемент | `O(1)` |
| `peek` / `top` | посмотреть верхний элемент | `O(1)` |

## Реализация через `list`

В Python для стека обычно достаточно списка: `append()` добавляет элемент, `pop()` удаляет последний.

```python
stack = []

stack.append(10)
stack.append(20)
stack.append(30)

print(stack[-1])  # 30 — верхний элемент
print(stack.pop())  # 30
print(stack.pop())  # 20
```

`append()` работает за амортизированное `O(1)`, а `pop()` с конца — за `O(1)`.

## Реализация через `collections.deque`

```python
from collections import deque

stack = deque()

stack.append(10)
stack.append(20)

print(stack.pop())  # 20
```

`deque` также даёт `O(1)` для добавления и удаления с обоих концов. Для обычного LIFO-стека `list` обычно достаточно.

## Стек вызовов

Python использует стек вызовов (`call stack`) для хранения активных вызовов функций: аргументов, локальных переменных и адреса возврата. При вызове функции создаётся новый стековый кадр, а после завершения функции он удаляется.
