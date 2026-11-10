# Учебные файлы для курса «Базовый минимум статистики»

Уроки лежат в `src/content/docs/practice/stats/`.

## Сборка

Нужен только `python3`. Запускайте из корня репозитория.

```bash
python3 scripts/stats-practice/build.py    # архив public/assets/practice/stats-practice.tar.gz
python3 scripts/stats-practice/charts.py   # графики public/assets/practice/stats/*.svg
```

Данные генерируются с фиксированным seed: содержимое файлов каждый раз одинаковое.
Графики рисуются из этих же данных. Запускайте `charts.py` после `build.py`.

## Важно

Ответы в уроках («Проверка») посчитаны на этих данных.
Если меняете генератор, пересчитайте ответы во всех уроках курса.
