---
title: "Параметры и аргументы функции"
prev: {"label":"Стек","link":"/interview/questions/python/collections/stack/"}
next: {"label":"Распаковка аргументов","link":"/interview/questions/python/functions/unpacking/"}
editUrl: false
---

Что такое параметры и аргументы функции? Какие виды параметров есть в Python?

## Ответ

**Параметры** — переменные, указанные при определении функции:

```python
def f(x):
    ...
```

**Аргументы** — значения, передаваемые при вызове функции:

```python
f(10)
```

## Виды параметров

### 1. Обязательные параметры

Обычные параметры можно передавать позиционно или по имени.

```python
def add(a, b):
    return a + b


result = add(5, 3)  # a=5, b=3
result = add(a=5, b=3)
```

### 2. Параметры со значениями по умолчанию

```python
def greet(name, greeting="Привет"):
    print(f"{greeting}, {name}!")


greet("Мария")                       # Использует значение по умолчанию
greet("Пётр", "Добро пожаловать")    # Передаёт другое значение
```

### 3. Переменное количество позиционных аргументов: `*args`

Одна звёздочка собирает лишние позиционные аргументы в кортеж.

```python
def sum_all(*numbers):
    return sum(numbers)


print(sum_all(1, 2, 3, 4, 5))  # 15
```

### 4. Переменное количество именованных аргументов: `**kwargs`

Две звёздочки собирают лишние именованные аргументы в словарь.

```python
def create_profile(**info):
    for key, value in info.items():
        print(f"{key}: {value}")


create_profile(name="Анна", age=30, city="Москва")
```

Значение имеет именно количество звёздочек, а не имя параметра: `*a` и `**kw` работают так же, как `*args` и `**kwargs`; `args` и `kwargs` — только общепринятые имена.

### 5. Только именованные параметры: keyword-only

Параметры после `*` разрешено передавать только по имени.

```python
def divide(a, b, *, precision=2):
    return round(a / b, precision)


result = divide(10, 3, precision=3)
```

Такой вызов вызовет `TypeError`:

```python
divide(10, 3, 3)
```

### 6. Только позиционные параметры: positional-only

Поддерживаются начиная с Python 3.8. Параметры перед `/` разрешено передавать только позиционно.

```python
def calculate(a, b, /):
    return a * b


result = calculate(5, 4)
```

Именованный вызов вызовет `TypeError`:

```python
calculate(a=5, b=4)
```

Порядок параметров в сигнатуре фиксирован: positional-only, обычные параметры, `*args`, keyword-only параметры, `**kwargs`. Нарушение порядка приводит к `SyntaxError`.

## Способы передачи аргументов

```python
def info(name, age, city):
    print(f"{name}, {age}, {city}")


# Позиционно: порядок важен
info("Иван", 28, "СПб")

# По имени: порядок не важен
info(city="Москва", name="Мария", age=32)

# Смешанный способ: позиционные аргументы идут первыми
info("Пётр", city="Казань", age=25)
```

## Распаковка аргументов

### Распаковка списка или кортежа через `*`

```python
data = ["Анна", 30, "Новосибирск"]

info(*data)
```

Эквивалентно:

```python
info("Анна", 30, "Новосибирск")
```

### Распаковка словаря через `**`

```python
person = {
    "name": "Олег",
    "age": 35,
    "city": "Екатеринбург",
}

info(**person)
```

Эквивалентно:

```python
info(name="Олег", age=35, city="Екатеринбург")
```

## Подводный камень: изменяемые значения по умолчанию

Значение по умолчанию создаётся один раз при определении функции. Поэтому один список повторно используется во всех вызовах.

Неправильно:

```python
def add_item(item, target_list=[]):
    target_list.append(item)
    return target_list
```

Правильно:

```python
def add_item(item, target_list=None):
    if target_list is None:
        target_list = []

    target_list.append(item)
    return target_list
```

## Уточнение для собеседования

Значение по умолчанию, обязательность и способ передачи — разные свойства параметра. Например, параметр может одновременно быть keyword-only и иметь значение по умолчанию.
