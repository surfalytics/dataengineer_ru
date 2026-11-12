---
name: practice-lesson
description: Write hands-on practice courses and lessons for the "Практика" section of dataengineer.ru - tasks with checks and hidden solutions, run locally on DuckDB (SQL) and Python. Use when the user asks for a new practice course, lesson, exercises, задания, or fixes to src/content/docs/practice/.
---

# Practice lesson (Практика)

Practice teaches by doing. The student installs tools on their own computer, runs every example, and solves tasks without AI.

Good examples to copy:
- SQL on DuckDB: `src/content/docs/practice/sql/intermediate/having.md`
- Python + SQL side by side: `src/content/docs/practice/stats/center.mdx`
- Python with DuckDB and Polars: `src/content/docs/practice/python/data-libs.mdx`
- Course start page: `src/content/docs/practice/sql/index.mdx`

## Tools

- **SQL: DuckDB.** CLI on the student's machine. No server, no browser editor. Dialect close to Postgres. If DuckDB syntax differs from Postgres, add a `:::note`.
- **Python: only when SQL is not enough** (files, API, statistics, automation). Python 3.10+, `uv` for projects. Libraries: standard library first, then DuckDB, Polars, PyArrow.
- When both fit, show both in `<Tabs syncKey="lang">` with `<TabItem label="Python">` and `<TabItem label="SQL">`. The page must be `.mdx` then.

## Course structure

Folder: `src/content/docs/practice/<course>/`.

| Page | What |
|---|---|
| `index.mdx` | О курсе: why the skill matters, who uses it (table by role), course plan, `<Steps>` "Как заниматься" |
| `setup.mdx` | Install tools and get the data. `<Tabs syncKey="os">` for macOS / Windows |
| lesson pages | One topic per page. `sidebar.order` sets the order |
| `final.md(x)` | Final project that uses the whole course |

Then:
1. Add the course to `src/nav.mjs` under "Практика".
2. Add a row and a `<LinkCard>` to `src/content/docs/practice/index.mdx`.

## Practice data

| Size | How |
|---|---|
| Small, one lesson | Create in the lesson with SQL `VALUES` / `generate_series` |
| Course files (CSV, Parquet) | Generator `scripts/<course>-practice/build.py` with a fixed seed. Output: `public/assets/practice/<course>-practice.tar.gz` |
| Big database (> 10 MB) | Build script in `scripts/<name>/`. Upload the file to a GitHub Release. Link `releases/latest/download/<file>` |

- Add a `README.md` in the script folder: how to build, what each file does.
- Answers in lessons are computed on this data. If you change the generator, recompute all answers.
- Use open data with a clear license, or generate it. List sources and licenses on a datasets page.

## Lesson page

Front matter:

```yaml
---
title: "HAVING"
head:
  - tag: title
    content: "HAVING в SQL: фильтр после GROUP BY | Инжиниринг Данных"
description: "<What the student learns, 70-160 chars>."
sidebar:
  order: 7
tags:
  - <course>
  - practice
---
```

Body, in this order:
1. Intro: 1-3 sentences. What the topic is and which tables or files we use.
2. Theory sections `## ...`: a short explanation, then a runnable example. Say what the result is ("Запрос вернёт 35 строк").
3. Comparison tables where they help (`WHERE` vs `HAVING`).
4. Starlight asides: `:::note` for dialect differences, `:::tip` for hints, `:::caution` for common mistakes.
5. `## Практика` (or `## Задания`). First line: `Решайте сами, без AI. Сначала напишите запрос, потом сверьтесь с проверкой, и только потом открывайте решение.`
6. 3-5 tasks:

````md
### Задание 1

<Task in one or two sentences. Name the table and columns.>

**Проверка:** 2 строки: 2007 и 2008.

<details>
<summary>Решение</summary>

```sql
SELECT ...
```

</details>
````

- **Проверка** gives a number the student can compare: row count, first row, a total. Never the full answer.
- Tasks go from easy to harder. The last one may combine with earlier lessons.

## Check before commit

- Run every code block. All numbers in the text and in "Проверка" must match the real output.
- SQL course: `python3 scripts/sql-tutorial-db/check_lessons.py <db.duckdb> src/content/docs/practice/sql`.
- Other courses: run each block by hand or with a small script in `scripts/<course>-practice/`.
- `npm run build` must pass.

## Writing rules

- Simple Russian, short sentences. Second person: "Установите", "Запустите".
- SQL keywords in UPPER CASE. One clause per line in longer queries.
- Code language in the fence: `sql`, `python`, `bash`. Output in a plain fence with no language.
- Links between lessons: root-absolute with a trailing slash, `/practice/python/environments/`.
