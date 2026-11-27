---
title: "Зачем метод возвращает self?"
prev: {"label":"classmethod и staticmethod","link":"/interview/questions/python/classes/method-types/"}
next: {"label":"Когда возвращают другой результат","link":"/interview/questions/python/classes/method-result/"}
editUrl: false
---

Зачем метод возвращает `self`?

## Ответ

Чтобы к результату можно было сразу приписать следующий вызов. Без этого метод отдаёт `None`, и вторая точка упадёт: `obj.set_a().set_b()` пожалуется, что у `None` нет метода `set_b`. Так устроен pandas: почти все методы возвращают датафрейм, поэтому и пишут `df.dropna().sort_values('x').head(10)`.
