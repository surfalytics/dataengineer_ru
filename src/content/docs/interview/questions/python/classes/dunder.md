---
title: "Дандер-методы (magic methods) в Python"
prev: {"label":"Миксины","link":"/interview/questions/python/classes/mixins/"}
next: {"label":"classmethod и staticmethod","link":"/interview/questions/python/classes/method-types/"}
editUrl: false
---

Что такое дандер-методы (Magic Methods) в Python?

## Ответ

Дандер-методы — от *double underscore* — это специальные методы Python, имена которых начинаются и заканчиваются двумя подчёркиваниями, например `__init__`, `__str__`, `__len__`, `__add__`.

Они позволяют определять или переопределять встроенное поведение объектов: инициализацию, строковое представление, сравнение, арифметические операции, доступ по индексу, работу контекстного менеджера и другие протоколы языка.
