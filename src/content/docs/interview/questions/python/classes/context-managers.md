---
title: "Контекстный менеджер: конструкция и предназначение"
prev: {"label":"Когда возвращают другой результат","link":"/interview/questions/python/classes/method-result/"}
next: {"label":"GIL","link":"/interview/questions/python/concurrency/gil/"}
editUrl: false
---

Контекстный менеджер (конструкция и предназначение).

## Ответ

Контекстный менеджер — это способ работать с ресурсами (например, файлами), не забывая их закрыть. Используется с `with`.

```python
with open("file.txt") as f:
    data = f.read()
```

После выхода из `with` файл автоматически закрывается, даже если произошла ошибка. Это безопаснее, чем писать вручную `f.close()`.

Для реализации контекстного менеджера мы должны реализовать методы `__enter__` и `__exit__`. Пример:

```python
class FileManager:
    def __init__(self, filename, mode):
        self.filename = filename
        self.mode = mode
        self.file = None

    def __enter__(self):
        print(f"Открываем файл {self.filename}")
        self.file = open(self.filename, self.mode)
        return self.file

    def __exit__(self, exc_type, exc_value, traceback):
        print(f"Закрываем файл {self.filename}")
        if self.file:
            self.file.close()

        # Возвращаем False, чтобы исключения не подавлялись
        return False


# Использование
with FileManager('test.txt', 'w') as f:
    f.write('Hello, World!')
```
