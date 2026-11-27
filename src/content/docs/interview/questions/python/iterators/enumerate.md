---
title: "Функция enumerate()"
prev: {"label":"Итераторы и генераторы","link":"/interview/questions/python/iterators/protocol/"}
next: {"label":"zip()","link":"/interview/questions/python/iterators/zip/"}
editUrl: false
---

Что делает функция `enumerate()`?

## Ответ

`enumerate(iterable, start=0)` добавляет счётчик к элементам итерируемого объекта и возвращает итератор пар `(индекс, значение)`.

- `iterable` — любой итерируемый объект.
- `start` — начальное значение счётчика; по умолчанию `0`.
- Результат вычисляется лениво: все пары не создаются заранее.

```python
fruits = ["apple", "banana", "mango"]

for index, fruit in enumerate(fruits):
    print(index, fruit)

# 0 apple
# 1 banana
# 2 mango
```

Начальный индекс можно изменить:

```python
for number, fruit in enumerate(fruits, start=1):
    print(number, fruit)

# 1 apple
# 2 banana
# 3 mango
```

`enumerate()` обычно понятнее и безопаснее ручного индексирования через `range(len(sequence))`:

```python
for index, value in enumerate(fruits):
    print(index, value)
```
