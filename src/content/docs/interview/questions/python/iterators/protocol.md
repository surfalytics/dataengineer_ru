---
title: "Итераторы и генераторы в Python"
prev: {"label":"Встроенные декораторы","link":"/interview/questions/python/functions/built-in-decorators/"}
next: {"label":"enumerate()","link":"/interview/questions/python/iterators/enumerate/"}
editUrl: false
---

Генератор, итератор

## Ответ

Итератор — объект, по которому можно проходить по одному элементу.

```python
it = iter([1, 2, 3])
print(next(it))  # 1
```

Протокол итерации требует двух методов:

- `__iter__()`: возвращает сам объект-итератор.
- `__next__()`: возвращает следующее значение или выбрасывает `StopIteration`.

Пример итератора (счетчик до `n`):

```python
class Counter:
    def __init__(self, low, high):
        self.current = low
        self.high = high

    def __iter__(self):
        return self  # Итератор возвращает сам себя

    def __next__(self):
        if self.current > self.high:
            raise StopIteration
        else:
            self.current += 1
            return self.current - 1
```

Генератор — это способ быстро создать итератор с `yield`:

```python
def my_gen():
    yield 1
    yield 2


for x in my_gen():
    print(x)
```

Генераторы экономят память — элементы создаются по мере запроса.
