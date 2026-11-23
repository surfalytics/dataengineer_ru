# Lead: whole-course work

Read this file only if you are the lead (the main session) or the Course step of the `lecture-summary` workflow. Lecture writers do not need it.

## Lead steps

1. **Prepare the source.** Run the `lecture-prep` workflow, or by hand: `fetch_transcripts.py` (see `scripts/lecture-tools/README.md`), then `words.py` on `<scratch>/src`.
2. **Make the glossary** `scripts/<prefix>-diagrams/glossary.md` before lecture 1, in the two-language form (see "Terms in two languages" in `SKILL.md`). For LLM and ML courses start from `scripts/cme295-diagrams/glossary.md`. Book glossaries keep most terms in English only: take their meanings and wrong forms, not their leading language.
3. **Set up `excb.py`** once per course, before the writers start: copy `scripts/data-quality-fundamentals-diagrams/excb.py` to `scripts/<prefix>-diagrams/`, set `OUT` to `public/assets/<course-slug>` and the scene name to `dataengineer_ru/<prefix>-{name}`. Parallel writers then do not race to copy it.
4. **Start one writer per lecture** (model `sonnet`, effort `high`). Give each writer only paths and numbers: transcript, slides text, video ID, glossary, lecture number and title, size target, previous and next lecture URLs, old page if any. The writer loads the skill itself.
5. **When the writers finish,** run the review, flow (if `LOW`) and clarity agents, one per lecture.
6. **Merge** `figures-lecNN.md`, `glossary-lecNN.md`, `README-lecNN.md` into `figures.md`, `glossary.md`, `README.md`. Delete the `-lecNN` files.
7. **Overview page** (below), `src/nav.mjs`, the row in `src/content/docs/lecture-summaries/index.md`.
8. **First course only:** create the section (below).
9. **EPUB:** follow the `book-epub` skill with `<course-slug>`: the link on the overview page, `node scripts/epub/build.mjs <course-slug>`, validation. The script finds courses in `lecture-summaries/` by itself.
10. Run `npm run build 2>&1 | tail -20` once at the end. Check that `dist/lecture-summaries/<group>/<course-slug>/index.html` exists.
11. **Status file:** set the PR number: `python3 -I scripts/book-tools/status.py <course-slug> --kind lecture --pr "#N"`.

## Overview page (`index.md`)

A planned course may already have a short page «О курсе» (`sidebar.label: "О курсе"`, a «скоро» badge in `src/nav.mjs`). Turn it into the full overview below: keep its facts and links, set `sidebar.label: "Обзор курса"`, remove the badge, and set «Статус» in `src/content/docs/lecture-summaries/index.md`. The template of a «О курсе» page: `src/content/docs/lecture-summaries/ai/stanford-cs336/index.md`.

Front matter:

```yaml
---
title: "<Course code>: <Course name> — конспект курса"
head:
  - tag: title
    content: "<Course code> на русском: конспект курса по <теме> | Инжиниринг Данных"   # max 70 chars
description: "Конспект курса <Course code> (<University>, <year>) на русском: <ключевые темы>. <K> лекций."
author: "<Lecturer 1>, <Lecturer 2>"   # short: the EPUB cover prints it
sidebar:
  order: 0
  label: "Обзор курса"
tags:
  - lectures
  - <topic>
---
```

Sections, in this order:

1. First paragraph: full course name, university, lecturers, term and year, number of lectures, links to the YouTube playlist and the course site. What the course teaches, in one sentence.
2. Note: `> Это подробный пересказ лекций на русском, а не перевод. Видео, слайды и задания — на сайте курса.`
3. The EPUB line: `📥 [Скачать конспект в EPUB](/downloads/<course-slug>.epub) — для телефона и электронной книги.`
4. Course map diagram: the blocks of the course and how they build on each other.
5. `## О чём курс простыми словами` - 2-4 paragraphs. What the course teaches. Who needs it. The main mental model.
6. `## Что нужно знать заранее` - bullets, with links to our pages if they exist (`/practice/python/`, `/practice/sql/`, a book summary).
7. `## Зачем проходить` - 4-6 bullets.
8. `## Как устроен курс` - table: Блок | Лекции | О чём. Then 2-3 sentences on how the course works: assignments, their size, what the lecturers expect (from the logistics part of lecture 1).
9. `## Главные идеи` - table: Идея | Лекция (with link).
10. `## Как учиться по конспекту` - the steps: read the page, watch the parts you need with the ▶ links, do `Практика`, answer the questions. Then reading paths per role (новичок, data engineer, ML engineer, руководитель) if the course is long.
11. `## Разбор по лекциям` - table: № | Лекция (link) | Что вы поймёте | Видео (duration).

## First course only: create the section

The section does not exist until the first course is written. Create it in the same PR as the first course:

1. `src/content/docs/lecture-summaries/index.md`:
   - front matter: `title: Конспекты лекций`, `head` title `Конспекты лекций Stanford и Harvard на русском | Инжиниринг Данных` (change the schools to the real ones), a `description` of 70-160 characters, `sidebar: {order: 1, label: Обзор}`, `tags: [lectures]`;
   - one paragraph on what is here, the note `> Это собственные пересказы лекций, а не переводы. Видео, слайды и задания — на сайте каждого курса.`;
   - `## Курсы` - table: Раздел | Курс (link) | О чём;
   - `## Как устроен конспект` - 4-5 bullets: overview page, lecture page with ▶ links to the video, diagrams, practice, questions with answers.
2. `src/nav.mjs`: a new topic «Конспекты лекций» right after «Конспекты книг»:

   ```js
   {
     label: 'Конспекты лекций',
     link: '/lecture-summaries/',
     icon: 'notes',
     match: ['/lecture-summaries/'],
     items: [
       { label: 'Обзор', link: '/lecture-summaries/' },
       {
         label: 'AI и ML',
         items: [
           {
             label: '<Course code>: <Course name>',
             collapsed: true,
             items: [{ autogenerate: { directory: 'lecture-summaries/ai/<course-slug>' } }],
           },
         ],
       },
     ],
   },
   ```

   Group labels: `ai` → `AI и ML`, `cs` → `Computer Science`, `data` → `Базы данных`.
3. `src/components/SectionGrid.astro`: a card `{ dir: 'lecture-summaries', title: 'Конспекты лекций', desc: '<one line>', href: '/lecture-summaries/', icon: 'notes', color: '#0969da' }` after the `ai` card.
4. Project `CLAUDE.md`: the row `| Конспекты лекций | lecture-summaries/ |` in the "Content Structure" table.
5. Header: `src/components/Header.astro` shows short tab labels at 800–1360 px (the `SHORT` map: «Конспекты лекций» → «Лекции»). Do not change it. A new tab with a long label needs a short label in that map.

## Check the whole course

- [ ] The overview page has all sections, `author:` in front matter, the note and the EPUB link.
- [ ] Lecture titles are the same in `title`, `sidebar.label`, the Previous/Next links and the overview tables.
- [ ] No two lectures draw the same diagram. If they do, keep it in the lecture that explains it more, link to it from the other one, and mark the extra one skipped in `figures.md`.
- [ ] The course is in `src/nav.mjs` and in the table of `src/content/docs/lecture-summaries/index.md`.
- [ ] The EPUB is built and checked with the `book-epub` skill.
- [ ] `npm run build` passes.
- [ ] The course's row in `scripts/lecture-tools/status.md` is current: status, date, PR, what is left.
