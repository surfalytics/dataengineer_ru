---
name: book-summary
description: Write a Russian book summary (конспект книги) for dataengineer.ru - one overview page plus one page per chapter under src/content/docs/book-summaries/. Use when the user asks to summarize a book, add a book or chapter to "Конспекты книг", or fix an existing summary.
---

# Book summary (конспект книги)

A book summary is a folder with an overview page and one page per chapter. It is our own retelling in simple Russian, not a translation.

Good examples to copy:
- `src/content/docs/book-summaries/engineering/data-warehouse-toolkit/` (diagrams + DuckDB practice)
- `src/content/docs/book-summaries/engineering/designing-data-intensive-applications/` (diagrams, no practice)
- `src/content/docs/book-summaries/business/lean-analytics/` (text only)

## Files

| What | Path |
|---|---|
| Overview | `src/content/docs/book-summaries/<group>/<book-slug>/index.md` |
| Chapter | `.../<book-slug>/NN-<chapter-slug>.md` (`01-...`, `02-...`) |
| Images | `public/assets/<book-slug>/chNN-<name>.png` |
| Diagram sources | `scripts/<book>-diagrams/` (see the `diagrams` skill) |

- `<group>`: `engineering`, `business`, `entrepreneurship`, or `ai` (create `ai/` when the first AI book comes).
- `<book-slug>`: English title in lowercase with hyphens.

## Steps

1. Create the folder, the overview, and all chapter pages.
2. Add the book to `src/nav.mjs` under "Конспекты книг", in the right group, as a `collapsed: true` item with `autogenerate`.
3. Add a row to the table in `src/content/docs/book-summaries/index.md`.
4. If the book is listed in `src/content/docs/resources/books.md`, link it to the summary.
5. Make diagrams with the `diagrams` skill. Check SQL blocks (see below).
6. Run `npm run build`.

## Overview page (`index.md`)

Front matter: `sidebar.order: 0`, `sidebar.label: "Обзор книги"`, `tags: [books, ...]`.

Sections, in this order:
1. First paragraph: full title, authors, publisher, year. What the book is about. How many chapters.
2. Note: `> Это собственный пересказ, а не перевод. За полным текстом идите в оригинал.`
3. `## Зачем читать` - 4-5 bullets.
4. `## Как устроена книга` - table: Часть | Главы | О чём.
5. Optional: `## Главные идеи` or a table of key techniques with links to chapters.
6. `## Как читать` - reading paths per role (новичок, analytics engineer, data engineer, руководитель).
7. If there is practice: `## Как работать с практикой`.
8. `## Разбор по главам` - table with a link to every chapter.

## Chapter page

Front matter:

```yaml
---
title: "<Book>, глава N: <Название главы по-русски>"
head:
  - tag: title
    content: "<Тема главы простыми словами> | Инжиниринг Данных"   # max 70 chars
description: "Конспект главы N <Book> на русском. <3-5 ключевых тем через запятую>."
sidebar:
  order: N
  label: "N. <Короткое название>"
tags:
  - books
  - <topic>
---
```

Body, in this order:
1. `**Главная мысль:** ...` - one or two sentences.
2. Main diagram right after it (if the chapter has one): `![<alt по-русски>](/assets/<book-slug>/chNN-<name>.png)`.
3. `## <Section>` blocks that follow the chapter. Use bullets and tables. 3-8 sections.
4. `## Ключевые термины` - table: Термин | Значение. English term, short Russian meaning.
5. `## Что это значит на практике` - bullets for a data engineer's daily work (`dbt`, warehouse, pipelines).
6. Optional `## Практика в DuckDB` (see below).
7. `## Вопросы для самопроверки` - 3-4 numbered questions.
8. Last line: `Предыдущая: [..](..). Следующая: [..](..).` with root-absolute links and a trailing slash.

## DuckDB practice inside a chapter

Use it for technical books where SQL shows the idea (modeling, SQL, ETL).

- Start: `Запустите \`duckdb\` в терминале или откройте [shell.duckdb.org](https://shell.duckdb.org). Блоки идут по порядку.`
- `### Шаг 1. Создаём ...` - create small tables with `VALUES` and `generate_series`. No files to download.
- `### Шаг 2. Проверяем` - a sanity query (row counts, "this must return 0 rows").
- `### Задания` - 3-4 tasks. Each solution is in `<details><summary>Решение</summary> ... </details>`, with one line that explains the result.
- All blocks run top to bottom in one in-memory session.
- Check the chapter: `python3 scripts/kimball-diagrams/check_sql.py <chapter.md>` (needs DuckDB CLI). It must print `OK`.

## Writing rules

- Retell in our words. Never paste text, tables, or figures from the book. Invent new example data.
- Simple Russian: short sentences, one idea per sentence.
- Keep terms in English with backticks when they are code-like: `grain`, `surrogate key`, `SCD2`.
- No `#` headings in the body. Start at `##`.
- One chapter page: about 80-250 lines. Cut filler.
