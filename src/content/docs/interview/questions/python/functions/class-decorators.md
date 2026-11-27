---
title: "Декораторы классов в Python"
prev: {"label":"Декораторы с аргументами","link":"/interview/questions/python/functions/decorators/"}
next: {"label":"Встроенные декораторы","link":"/interview/questions/python/functions/built-in-decorators/"}
editUrl: false
---

Что такое декоратор класса?

## Ответ

Декоратор класса — это функция, которая принимает класс как аргумент и может изменить, расширить или заменить его. Декоратор применяется во время выполнения инструкции `class`, до создания экземпляров класса.

В Python он используется аналогично декоратору функции: запись `@decorator_name` размещается непосредственно перед определением класса.

```python
@decorator_name
class MyClass:
    ...
```

## Можно ли передать декоратору сам класс?

Да. Если поставить `@register` над объявлением класса, Python передаст созданный класс в `register`. Зарегистрируем класс и вернём его, чтобы под именем `Report` по-прежнему можно было создавать экземпляры.

```python
registry = {}

def register(cls):
    registry[cls.__name__] = cls
    return cls

@register
class Report:
    pass

assert registry["Report"] is Report
assert isinstance(Report(), Report)
```

`@register` над классом эквивалентно `Report = register(Report)`. У [фабрики декораторов](/interview/questions/python/functions/decorators/) другая роль: в `@convert_result(int)` класс `int` настраивает поведение обёртки.
