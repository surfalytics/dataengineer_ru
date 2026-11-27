---
title: "Garbage collector и циклические ссылки"
prev: {"label":"Поверхностная и глубокая копия","link":"/interview/questions/python/objects/copy/"}
next: {"label":"Освобождение памяти","link":"/interview/questions/python/objects/memory/"}
editUrl: false
---

Что такое garbage collector? Что такое цикличные ссылки?

## Ответ

Garbage collector (GC) — автоматическая система удаления объектов, на которые больше никто не ссылается.

**Циклические ссылки** — объекты, которые ссылаются друг на друга:

```python
a = []
b = []
a.append(b)
b.append(a)
```

Они "держат" друг друга, хотя больше никому не нужны. Python умеет находить такие циклы и удалять.
