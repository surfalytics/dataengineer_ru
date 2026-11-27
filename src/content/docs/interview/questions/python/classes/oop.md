---
title: "Три принципа ООП в Python"
prev: {"label":"Освобождение памяти","link":"/interview/questions/python/objects/memory/"}
next: {"label":"Миксины","link":"/interview/questions/python/classes/mixins/"}
editUrl: false
---

Три принципа ООП и в чем их суть?

## Ответ

**Инкапсуляция** — прячем внутренности объекта (переменные, методы) от внешнего мира.

```python
class BankAccount:
    def __init__(self):
        self.__balance = 0  # скрытая переменная

    def deposit(self, amount):
        self.__balance += amount

    def get_balance(self):
        return self.__balance


# Пользователь не может напрямую изменить __balance, только через методы
```

**Наследование** — создаём класс на основе другого, повторно используя код.

```python
class Animal:
    def speak(self):
        print("Some sound")


class Dog(Animal):
    def speak(self):
        print("Woof")


# Dog унаследовал метод speak, но переопределил его.
```

**Полиморфизм** — одинаковые методы работают по-разному в разных классах.

```python
animals = [Dog(), Animal()]
for animal in animals:
    animal.speak()  # У Dog — "Woof", у Animal — "Some sound"
```
