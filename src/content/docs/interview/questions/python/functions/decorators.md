---
title: "Декораторы в Python"
prev: {"label":"Области видимости","link":"/interview/questions/python/functions/scope/"}
next: {"label":"Декораторы классов","link":"/interview/questions/python/functions/class-decorators/"}
editUrl: false
---

Что такое декоратор?

## Ответ

Функция, которая берёт функцию и возвращает обёрнутую, чтобы добавить поведение, не трогая тело: логирование, замер времени, кеш. Строчка `@timer` над функцией `load_data` — это просто короткая запись для `load_data = timer(load_data)`. Отсюда и засада: имя теперь указывает на обёртку, поэтому `load_data.__name__` вернёт не "load\_data", и `help` врёт. Чинится строчкой `functools.wraps`.

## Можно ли передать декоратору аргументы, в том числе класс?

Да. Запись `@convert_result(int)` вызывает **фабрику декораторов** при определении функции. Фабрика получает класс `int` и возвращает декоратор. Сам декоратор получает исходную функцию. Позднее, при вызове `quantity("42")`, строку `"42"` получает уже обёртка.

```python
from functools import wraps

def convert_result(result_type):
    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            value = func(*args, **kwargs)
            return result_type(value)
        return wrapper
    return decorate

@convert_result(int)
def quantity(text):
    return text.strip()

assert quantity(" 42 ") == 42
assert quantity.__name__ == "quantity"
```

Здесь `int` передан как объект класса, без создания экземпляра в строке декоратора. Эквивалентная запись применения — `quantity = convert_result(int)(quantity)`. Класс также может быть самим декорируемым объектом: так работает [декоратор класса](/interview/questions/python/functions/class-decorators/).
