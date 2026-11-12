---
title: "DuckDB: Up and Running — конспект книги"
head:
  - tag: title
    content: "DuckDB: Up and Running — конспект и SQL | Инжиниринг Данных"
description: "Конспект DuckDB: Up and Running (Wei-Meng Lee) на русском. CSV, Parquet, JSON, Polars, JupySQL, httpfs, MotherDuck. SQL-практика в каждой главе."
author: "Wei-Meng Lee"
sidebar:
  order: 0
  label: "Обзор книги"
tags:
  - books
  - duckdb
  - sql
---

**DuckDB: Up and Running. Fast Data Analytics and Reporting** — книга Wei-Meng Lee (O'Reilly, 2025). Она учит работать с DuckDB: встроенной аналитической базой, которая запускается без сервера. В книге 9 глав. Они идут от установки и импорта файлов до Polars, JupySQL, удалённых данных и облака MotherDuck.

> Это собственный пересказ, а не перевод. За полным текстом идите в оригинал. Данные для SQL придуманы заново.

## Зачем читать

- DuckDB читает CSV, Parquet и JSON прямо из файлов. Загрузка в базу не нужна.
- Это быстрый способ изучить SQL и проверить идею на локальной машине.
- DuckDB работает в одном процессе с Python. Он понимает `pandas` и Polars DataFrame.
- Те же запросы идут по файлам в S3, на GitHub и в Hugging Face через `httpfs`.
- Книга короткая и практичная. Хорошая точка входа для analytics engineer и data engineer.

## Как устроена книга

| Часть | Главы | О чём |
|---|---|---|
| Основы | 1–3 | Что такое DuckDB, импорт данных, CLI и SQL |
| Python и анализ | 4–5 | Polars, EDA, геоанализ с расширением `spatial` |
| Форматы и среда | 6–7 | JSON, JupySQL и графики |
| Данные вне ноутбука | 8–9 | Удалённые файлы, Hugging Face, MotherDuck |

## Как читать

- **Новичок.** Главы 1–3. Потом глава 5 как пример анализа.
- **Analytics engineer.** Главы 2, 3, 6 и 8. Это работа с файлами и форматами.
- **Data engineer.** Главы 2, 4, 8 и 9. Они про интеграции и облако.
- **Руководитель.** Глава 1: когда DuckDB подходит, а когда нужен сервер.

## Как работать с практикой

- Установите DuckDB: `brew install duckdb` или откройте [shell.duckdb.org](https://shell.duckdb.org).
- Данные создаются SQL-кодом. Большие файлы скачивать не нужно.
- Блоки идут по порядку. Выполняйте их сверху вниз в одной сессии.
- Блоки для сети и облака (`https://`, `hf://`, `md:`) помечены. Их нельзя выполнить без доступа или аккаунта.

## Разбор по главам

| Глава | Тема |
|---|---|
| [1. Старт с DuckDB](/book-summaries/engineering/duckdb-up-and-running/01-getting-started/) | Что такое DuckDB, первые запросы, почему он быстрый |
| [2. Импорт данных](/book-summaries/engineering/duckdb-up-and-running/02-importing-data/) | CSV, Parquet, Excel, MySQL |
| [3. Основы SQL](/book-summaries/engineering/duckdb-up-and-running/03-sql-primer/) | CLI, dot commands, таблицы, join, агрегаты |
| [4. DuckDB и Polars](/book-summaries/engineering/duckdb-up-and-running/04-polars/) | DataFrame, lazy evaluation, SQL по DataFrame |
| [5. EDA и геоанализ](/book-summaries/engineering/duckdb-up-and-running/05-eda-spatial/) | Анализ задержек рейсов, расширение `spatial` |
| [6. JSON](/book-summaries/engineering/duckdb-up-and-running/06-json/) | Загрузка и экспорт JSON, вложенные данные |
| [7. JupySQL](/book-summaries/engineering/duckdb-up-and-running/07-jupysql/) | SQL в Jupyter, графики |
| [8. Удалённые данные](/book-summaries/engineering/duckdb-up-and-running/08-remote-data/) | `httpfs`, GitHub, Hugging Face |
| [9. MotherDuck](/book-summaries/engineering/duckdb-up-and-running/09-motherduck/) | DuckDB в облаке, общий доступ, hybrid queries |
