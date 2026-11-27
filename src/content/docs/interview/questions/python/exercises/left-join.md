---
title: "Задача 2. LEFT JOIN двух списков"
prev: {"label":"Задача 1. Список по умолчанию","link":"/interview/questions/python/exercises/mutable-default/"}
next: false
editUrl: false
---

Даны два списка пар. Слева — `(id, имя)`, справа — `(id, город)`. Напишите функцию, которая вернёт строки `(id, имя, город)` по правилам SQL `LEFT JOIN … ON l.id = r.id`. Числовые ключи могут повторяться с обеих сторон. `None` обозначает SQL `NULL` и при обычном равенстве ни с чем не соединяется. Порядок результата для проверки не важен.

```python
left = [(1, "Анна"), (2, "Борис"), (2, "Вера"), (3, "Лев")]
right = [(2, "Омск"), (2, "Тула"), (4, "Пермь")]
```

<details>
<summary>Сколько строк получится?</summary>

| id | Имя | Город |
| ---: | --- | --- |
| 1 | Анна | None |
| 2 | Борис | Омск |
| 2 | Борис | Тула |
| 2 | Вера | Омск |
| 2 | Вера | Тула |
| 3 | Лев | None |

Две левые строки с ключом 2 встречают две правые — это **четыре пары**. Анна и Лев добавляют ещё по строке. У Перми нет пары слева, поэтому её в результате нет.

</details>

## Nested Loop — перебрать пары

Для каждой левой строки просматриваем весь правый список. Строку с `None` добавляем **после завершения внутреннего цикла**, только если совпадений не было.

```python
def nested_left_join(left, right):
    result = []
    for key, name in left:
        matched = False
        for right_key, city in right:
            if key is not None and key == right_key:
                result.append((key, name, city))
                matched = True
        if not matched:
            result.append((key, name, None))
    return result
```

## Hash Join — построить индекс справа

В словаре храним **список городов для каждого ключа**. Если хранить только последний город, потеряются совпадения. Ключи `None` справа пропускаем.

```python
def hash_left_join(left, right):
    cities_by_id = {}
    for key, city in right:
        if key is not None:
            cities_by_id.setdefault(key, []).append(city)

    result = []
    for key, name in left:
        cities = cities_by_id.get(key)
        if cities is None:
            result.append((key, name, None))
        else:
            result.extend((key, name, city) for city in cities)
    return result
```

## Merge Join — двигаться по отсортированным ключам

Сортируем копии входов. Указатель `start` пропускает правые строки с меньшим ключом. Для каждой левой строки временный указатель `pos` выдаёт всю группу совпадений. Если следующий левый ключ тот же, его поиск начинается с той же позиции `start`. Так обе строки с ключом 2 получают оба города.

```python
def merge_left_join(left, right):
    left_rows = sorted(left, key=lambda row: (row[0] is None, row[0]))
    right_rows = sorted(
        (row for row in right if row[0] is not None),
        key=lambda row: row[0],
    )
    result = []
    start = 0
    for key, name in left_rows:
        if key is None:
            result.append((key, name, None))
            continue
        while start < len(right_rows) and right_rows[start][0] < key:
            start += 1

        pos = start
        while pos < len(right_rows) and right_rows[pos][0] == key:
            result.append((key, name, right_rows[pos][1]))
            pos += 1
        if pos == start:
            result.append((key, name, None))
    return result
```

## Как выбрать решение?

Пусть `L` и `R` — размеры входов, `K` — число результирующих строк. Все три функции дополнительно выделяют `O(K)` памяти под ответ.

| Алгоритм | Время | Память сверх результата |
| --- | --- | --- |
| Nested Loop | `O(L × R + L)` | `O(1)` |
| Hash Join | В среднем `O(L + R + K)` | `O(R)` для индекса |
| Merge Join | `O(L log L + R log R + K + L + R)` с сортировкой. На уже отсортированных списках проход занимает `O(L + R + K)` | Представленная версия использует `O(L + R)` для сортировки. Для прохода по готовым отсортированным спискам достаточно указателей. |

Для коротких списков проще проверить перебор. Для несортированных данных с хешируемыми ключами обычно удобен словарь. Если входы уже отсортированы по ключу, можно сразу выполнить слияние. При множестве повторов любой алгоритм должен выдать все `K` пар. [Та же задача на SQL](/interview/questions/sql/joins/using-id/)
