# Учебная база для курса «Базовый минимум SQL»

Скрипты собирают файл `sql-tutorial.duckdb` для уроков в `src/content/docs/practice/sql/`.
Схемы и имена таблиц повторяют SQL Tutorial от ThoughtSpot (Mode): `tutorial.*` и `benn.*`.

## Сборка

Нужны `python3` (с `openpyxl`) и DuckDB CLI 1.2+.

```bash
scripts/sql-tutorial-db/build.sh
```

Результат: `scripts/sql-tutorial-db/.cache/sql-tutorial.duckdb` (около 40 МБ).
Папка `.cache` не попадает в git.

## Файлы

| Файл | Что делает |
|---|---|
| `fetch.py` | Скачивает открытые данные в `.cache/raw` |
| `prepare.py` | Готовит CSV из сырых данных в `.cache/csv` |
| `generate_football.py` | Генерирует игроков студенческого футбола |
| `generate_yammer.py` | Генерирует данные Yammer для аналитических кейсов |
| `yammer_checks.sql` | Запросы, которые проверяют выводы кейсов на данных Yammer |
| `build.sql` | Создаёт таблицы и представления в DuckDB |
| `build.sh` | Запускает всё по порядку |
| `check_lessons.py` | Выполняет все SQL-блоки из уроков и сообщает об ошибках |

## Проверить уроки

```bash
python3 scripts/sql-tutorial-db/check_lessons.py scripts/sql-tutorial-db/.cache/sql-tutorial.duckdb src/content/docs/practice/sql
```

## Публикация

Файл базы большой, поэтому его нет в репозитории. Он лежит в GitHub Release.
Ссылка в уроках: `https://github.com/surfalytics/dataengineer_ru/releases/latest/download/sql-tutorial.duckdb`.

```bash
gh release create sql-tutorial-v1 scripts/sql-tutorial-db/.cache/sql-tutorial.duckdb \
  --title "Учебная база SQL" --notes "База для курса «Базовый минимум SQL»"
```

Чтобы обновить базу, загрузите новый файл в релиз: `gh release upload <tag> <file> --clobber`.

## Источники и лицензии

См. страницу «Учебные данные» на сайте: `src/content/docs/practice/sql/datasets.md`.
Crunchbase — CC BY-NC 4.0, только некоммерческое использование.
