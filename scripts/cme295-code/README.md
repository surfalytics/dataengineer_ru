# Код курса CME295

Запуск из корня: `python3 -I scripts/cme295-code/<файл>.py`. Зависимости: `requirements.txt`.

## Лекция 1

Код и вывод на странице совпадают с файлами. Проверка: `python3 -I scripts/lecture-tools/check_code.py <страница.md> scripts/cme295-code --prefix lec01 --python <venv>/bin/python`.

| Лекция | Пример | Файл | Статус |
|---|---|---|---|
| 1 | BPE на маленьком корпусе | lec01_bpe.py | ok |
| 1 | Self-attention и causal mask на numpy | lec01_attention.py | ok |
| 1 | Задача 1: токенизатор по слияниям BPE | lec01_task1.py | ok |
| 1 | Задача 2: синусоидальный positional embedding | lec01_task2.py | ok |
| 1 | Задача 3: деление на sqrt(d_k) | lec01_task3.py | ok |
