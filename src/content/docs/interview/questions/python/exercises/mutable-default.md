---
title: "Задача 1. Список по умолчанию"
prev: {"label":"Линтеры","link":"/interview/questions/python/algorithms/linters/"}
next: {"label":"Задача 2. LEFT JOIN двух списков","link":"/interview/questions/python/exercises/left-join/"}
editUrl: false
---

Что напечатает каждый вызов? Функция добавляет в `test` список из двух аргументов. В третьем вызове явно передаётся пустой список, в четвёртом — уже заполненный.

```python
def test_na_duraka(a, b, test=[]):
    test.append([a, b])
    return test

print(test_na_duraka(1, 1))
print(test_na_duraka(2, 3))
empty = []
print(test_na_duraka(4, 5, test=empty))
print(test_na_duraka(6, 7, test=[[0, 0]]))
print(test_na_duraka(8, 9))
```

<details>
<summary>Показать вывод и разбор</summary>

```text
[[1, 1]]
[[1, 1], [2, 3]]
[[4, 5]]
[[0, 0], [6, 7]]
[[1, 1], [2, 3], [8, 9]]
```

Значение по умолчанию `[]` создаётся **один раз, когда выполняется определение функции**. Первый, второй и пятый вызовы изменяют один и тот же список. Третий и четвёртый получили собственные списки. После третьего вызова переменная `empty` содержит `[[4, 5]]`, поскольку `append` изменил переданный объект.

</details>

## Как написать правильно?

Пусть вызов без списка каждый раз начинает с пустого, а явно переданный список по-прежнему пополняется.

```python
def test_na_duraka(a, b, test=None):
    if test is None:
        test = []
    test.append([a, b])
    return test

assert test_na_duraka(1, 1) == [[1, 1]]
assert test_na_duraka(2, 3) == [[2, 3]]

empty = []
assert test_na_duraka(4, 5, test=empty) is empty
assert empty == [[4, 5]]
```

Проверка `is None` сохраняет переданный пустой список. При `if not test` пустой список тоже прошёл бы условие, функция подменила бы его новым, а переменная `empty` у вызывающего осталась бы пустой. [Значения аргументов по умолчанию](https://docs.python.org/3/faq/programming.html#why-are-default-values-shared-between-objects)
