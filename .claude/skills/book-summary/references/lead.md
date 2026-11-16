# Lead: whole-book work

Read this file only if you are the lead (the main session). Chapter workers do not need it.

## Lead steps

1. **Prepare the source.** Split the book into chapter text files (see "Save tokens" in `SKILL.md`). Count the words of each chapter with `words.py`.
2. **Make the glossary** `scripts/<book>-diagrams/glossary.md` before chapter 1.
3. **Start one worker per chapter** (model `sonnet`, effort `high`). Give each worker only: the path to its `chNN.txt`, the book slug, the glossary path, the chapter number and title, the source word count and the size target, the previous and next chapter URLs, and the path of the old page if one exists. Do not paste book text or the skill into the prompt: the worker loads the skill itself.
4. **When the workers finish,** run the `ru-proofread` review and flow agents, one agent per chapter (see the `ru-proofread` skill for models). A worker never reviews its own text.
5. **Merge** `figures-chNN.md`, `glossary-chNN.md`, `README-chNN.md` into the registers.
6. Overview page, `src/nav.mjs` (`collapsed: true` item with `autogenerate`), row in `src/content/docs/book-summaries/index.md`, `author:` in front matter, and the **cover** (see below). Never skip the cover: without the file the carousel draws a plain placeholder from the title. The home page carousel (`src/components/BookCarousel.astro`) picks the book up from `src/nav.mjs`.
7. If the book is listed in `src/content/docs/resources/books.md`, link it to the summary.
8. **Build and check the EPUB** with the `book-epub` skill: link on the overview page, build, validate. Do this for a new book and after any change to a chapter.
9. Run `npm run build 2>&1 | tail -20` once at the end, not in parallel.
10. **Status file:** set the PR number in `scripts/book-tools/status.md`: `python3 -I scripts/book-tools/status.py <slug> --pr "#N"`. The workflow fills the other columns. After work by hand, run it with `--scratch` and `--chapters`, or with `--status` and `--left`.

## Parallel work

- One worker per chapter is fine. Workers must not edit shared files (`index.md`, `nav.mjs`, registers). They write `figures-chNN.md`, `glossary-chNN.md`, `README-chNN.md`. The lead merges them.
- Proofreading with parallel workers: each worker runs `scripts/ru-proofread/check.py` on its own chapter. The lead starts the review and flow agents (`ru-proofread` skill) after the workers finish, one agent per chapter. A worker never reviews its own text.

## Cover (carousel thumbnail)

Every book needs a cover file. The home page carousel (`src/components/BookCarousel.astro`) shows `public/assets/book-covers/<book-slug>.jpg` and the book title and `author:` from `index.md`. If the file is missing, the carousel shows a generated placeholder. That is a bug, not a fallback to accept.

1. Get the cover image: page 1 of the PDF (`pdftoppm -f 1 -l 1 -r 150 -png <book.pdf> <scratch>/cover`), the cover file inside an EPUB, or the publisher's cover image if the user gives it. Work in the scratchpad, not in the repo.
2. Resize and compress with `sharp`: width 240px, progressive JPEG, quality about 70, under 30 KB:

```bash
node -e "require('sharp')(process.argv[1]).resize({width:240}).jpeg({quality:70,progressive:true,mozjpeg:true}).toFile(process.argv[2])" <scratch>/cover-1.png public/assets/book-covers/<book-slug>.jpg
```

3. **Look at the JPEG** with the `Read` tool. It must show the real cover, not a blank page, a copyright page, or a crop.
4. The file name must match the book folder name: for `book-summaries/engineering/data-quality-fundamentals` the file is `data-quality-fundamentals.jpg`. A different name means no cover.
5. After `npm run build`, check that the book is in the carousel: `grep -c "<book-slug>.jpg" dist/index.html` must print 1 or more.
6. If you cannot get a cover (no PDF, scanned file without a cover page), say so in the final report. Do not leave it silent.

## Overview page (`index.md`)

Front matter: `sidebar.order: 0`, `sidebar.label: "Обзор книги"`, `author: "<Имя Автора>"`, `tags: [books, ...]`.

Sections, in this order:
1. First paragraph: full title, authors, publisher, year. What the book is about. How many chapters.
2. Note: `> Это подробный пересказ на русском, а не перевод. За полным текстом идите в оригинал.`
3. Book map diagram.
4. `## О чём книга простыми словами` - 2-4 paragraphs. What problem the book solves. Who has this problem. The main mental model of the book.
5. `## Что нужно знать заранее` - bullets, with links to our pages if they exist.
6. `## Зачем читать` - 4-6 bullets.
7. `## Как устроена книга` - table: Часть | Главы | О чём. Then a few sentences on how the parts connect.
8. `## Главные идеи` - table: Идея | Глава (with link).
9. `## Как читать` - reading paths per role (новичок, analytics engineer, data engineer, руководитель).
10. If there is practice: `## Как работать с практикой`.
11. `## Разбор по главам` - table with a link to every chapter and one sentence on what the chapter answers.

## Check the whole book

For the whole book, answer yes to all:

- [ ] `public/assets/book-covers/<book-slug>.jpg` exists, is 240px wide, under 30 KB, and you looked at it.
- [ ] The book is listed in `src/nav.mjs` and the built `dist/index.html` contains its cover file name (the carousel shows it).
- [ ] `index.md` has `author:` in front matter (the carousel prints it under the title).
- [ ] The EPUB is built and checked with the `book-epub` skill, and the overview page has the download link.
- [ ] `npm run build` passes.
- [ ] The book's row in `scripts/book-tools/status.md` is current: status, date, PR, what is left.
