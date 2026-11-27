---
title: "Почему сортировка сравнением не быстрее O(n log n)"
prev: {"label":"Сортировка в Python","link":"/interview/questions/python/algorithms/python-sort/"}
next: {"label":"QuickSort, MergeSort и HeapSort","link":"/interview/questions/python/algorithms/sort-comparison/"}
editUrl: false
---

Почему нельзя сортировать быстрее n log n?

## Ответ

Потому что это доказанная граница для сортировки сравнениями. Обойти её можно, только если перестать сравнивать: `counting` раскладывает по частотам, `radix` по разрядам, оба дают линейное время, но работают лишь для целых из ограниченного диапазона. В питоне под капотом Timsort: ищет уже готовые упорядоченные куски, поэтому на почти отсортированных данных летает.
