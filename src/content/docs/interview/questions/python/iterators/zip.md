---
title: "Функция zip()"
prev: {"label":"enumerate()","link":"/interview/questions/python/iterators/enumerate/"}
next: {"label":"Динамическая и сильная типизация","link":"/interview/questions/python/objects/typing/"}
editUrl: false
---

Что делает функция `zip()`?

## Ответ

`zip()` объединяет несколько итерируемых объектов по позициям и возвращает итератор кортежей вида `(element_1, element_2, ...)`.

Результат вычисляется лениво: все кортежи не создаются заранее.

```python
a = [1, 2, 3]
b = ["a", "b", "c", "d"]

print(list(zip(a, b)))
# [(1, "a"), (2, "b"), (3, "c")]

for elements in zip(a, b):
    print(elements)

# (1, "a")
# (2, "b")
# (3, "c")
```

## Последовательности разной длины

По умолчанию `zip()` завершает итерацию вместе с самой короткой последовательностью. Оставшиеся элементы длинных последовательностей игнорируются.

Если различие длин является ошибкой, начиная с Python 3.10 можно использовать `strict=True`:

```python
a = [1, 2, 3]
b = ["a", "b"]

list(zip(a, b, strict=True))
# ValueError: zip() argument 2 is shorter than argument 1
```

## Практический пример

`zip()` удобно использовать для построения словаря из отдельных списков ключей и значений:

```python
keys = ["name", "age", "city"]
values = ["Анна", 30, "Москва"]

person = dict(zip(keys, values))
print(person)
# {"name": "Анна", "age": 30, "city": "Москва"}
```

## Обратная операция

Последовательность пар можно разделить обратно с помощью распаковки `*`:

```python
pairs = [(1, "a"), (2, "b"), (3, "c")]

numbers, letters = zip(*pairs)

print(numbers)  # (1, 2, 3)
print(letters)  # ("a", "b", "c")
```
