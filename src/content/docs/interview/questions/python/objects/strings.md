---
title: "Почему строку нельзя изменить по индексу"
prev: {"label":"Равенство и идентичность","link":"/interview/questions/python/objects/equality/"}
next: {"label":"Почему присваивание не копирует список","link":"/interview/questions/python/objects/assignment/"}
editUrl: false
---

Что будет в результате этого кода?

```python
s = 'Hello world'
s[5] = 'a'
```

## Ответ

Ошибка `TypeError: 'str' object does not support item assignment` — строки в Python неизменяемые.
