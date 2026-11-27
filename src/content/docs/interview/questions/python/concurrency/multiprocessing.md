---
title: "Multiprocessing в Python"
prev: {"label":"Потоки и процессы","link":"/interview/questions/python/concurrency/threads-processes/"}
next: {"label":"Что такое асинхронность?","link":"/interview/questions/python/concurrency/asynchrony/"}
editUrl: false
---

Что такое multiprocessing?

## Ответ

Далее рассматривается обычная сборка CPython с включённым GIL.

`multiprocessing` — это модуль Python для параллельного выполнения кода в **нескольких процессах**, а не потоках. Каждый процесс имеет **свой интерпретатор и свой GIL**, поэтому multiprocessing позволяет **реально задействовать несколько ядер CPU** в отличие от многопоточности в Python, которая ограничена GIL.

- В Python многопоточность не даёт параллельной работы вычислительных задач, т.к. есть GIL (Global Interpreter Lock).
- `multiprocessing` запускает **отдельные процессы**, каждый со **своим GIL**, поэтому могут работать параллельно на разных ядрах.
