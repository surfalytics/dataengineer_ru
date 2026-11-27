---
title: "Зачем нужны @classmethod и @staticmethod?"
prev: {"label":"Специальные методы","link":"/interview/questions/python/classes/dunder/"}
next: {"label":"Когда возвращают self","link":"/interview/questions/python/classes/return-self/"}
editUrl: false
---

Зачем нужны `@classmethod` и `@staticmethod`?

## Ответ

### Обычный метод — `self`

```python
class MyClass:
    def instance_method(self):
        # Получает экземпляр (self)
        pass
```

### `@classmethod`

Получает класс (`cls`) вместо экземпляра.

```python
class Date:
    def __init__(self, year, month, day):
        self.year = year
        self.month = month
        self.day = day

    @classmethod
    def from_string(cls, date_string):
        # Альтернативный конструктор
        year, month, day = map(int, date_string.split('-'))
        return cls(year, month, day)  # Создаёт экземпляр


# Использование
d = Date.from_string('2024-01-15')
```

Зачем:

- Альтернативные конструкторы (factory methods)
- Работа с атрибутами класса
- Правильно работает с наследованием (получает нужный класс)

### `@staticmethod`

Не получает ни `self`, ни `cls` — обычная функция внутри класса.

```python
class Math:
    @staticmethod
    def add(x, y):
        # Просто функция, нет доступа к классу или экземпляру
        return x + y


# Использование
result = Math.add(5, 3)
```

Зачем:

- Утилитарные функции, логически связанные с классом
- Группировка функций в namespace класса
- Не нужен доступ к данным класса/экземпляра

### Сравнение

| Тип | Первый параметр | Доступ к | Использование |
| --- | --- | --- | --- |
| Обычный метод | `self` | экземпляр | работа с данными объекта |
| `@classmethod` | `cls` | класс | альтернативные конструкторы |
| `@staticmethod` | нет | ничего | утилитарные функции |

### На собеседовании важно

- `@classmethod` используется для factory methods и работы с классом
- `@staticmethod` просто группирует функции в namespace класса
