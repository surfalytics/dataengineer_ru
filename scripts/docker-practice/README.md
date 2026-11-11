# Учебные файлы для курса «Базовый минимум Docker»

Скрипт собирает архив `public/assets/practice/docker-practice.tar.gz` для уроков в `src/content/docs/practice/docker/`.
Ученики скачивают его по адресу `https://dataengineer.ru/assets/practice/docker-practice.tar.gz`.

## Сборка

Нужен только `python3`. Запускайте из корня репозитория.

```bash
python3 scripts/docker-practice/build.py
```

Данные генерируются с фиксированным seed: содержимое файлов каждый раз одинаковое.

## Важно

Ответы в уроках («Проверка») посчитаны на этих данных.
Если меняете генератор или скрипты, пересчитайте ответы во всех уроках курса.
