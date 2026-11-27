---
title: "Чем QuickSort, MergeSort и HeapSort отличаются на практике?"
prev: {"label":"Нижняя граница сортировки","link":"/interview/questions/python/algorithms/sort-bound/"}
next: {"label":"Линтеры","link":"/interview/questions/python/algorithms/linters/"}
editUrl: false
---

Чем QuickSort, MergeSort и HeapSort отличаются на практике?

## Ответ

QuickSort в среднем самый шустрый и работает на месте, но на неудачных данных проваливается в n². MergeSort всегда n log n и стабильный, равные элементы не переставляет, зато требует дополнительную память под копию. HeapSort даёт n log n без лишней памяти, но не стабильный и на деле медленнее из-за прыжков по памяти.
