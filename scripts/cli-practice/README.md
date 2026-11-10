# Учебные файлы для курса «Базовый минимум CLI»

Скрипт собирает архив `public/assets/practice/cli-practice.tar.gz` для уроков в `src/content/docs/practice/cli/`.
Ученики скачивают его по адресу `https://dataengineer.ru/assets/practice/cli-practice.tar.gz`.

## Сборка

Нужен только `python3`.

```bash
python3 scripts/cli-practice/build.py
```

Данные генерируются с фиксированным seed: содержимое файлов каждый раз одинаковое.

## Важно

Ответы в уроках («Проверка») посчитаны на этих данных.
Если меняете генератор, пересчитайте ответы во всех уроках курса.
