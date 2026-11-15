---
name: book-summary
description: Write a Russian book summary (конспект книги) for dataengineer.ru - a detailed Russian retelling of a book, one overview page plus one page per chapter, with diagrams, under src/content/docs/book-summaries/. Use when the user asks to summarize or translate a book, add a book or chapter to "Конспекты книг", or fix or expand an existing summary.
---

# Book summary (конспект книги)

A book summary is a detailed Russian retelling of a book. It is a folder with an overview page and one page per chapter, with diagrams.

## The goal

- **Reader:** a Russian-speaking data engineer who has NOT read the book and may not know its field.
- **Goal:** the reader gets the full core content of the book in clear Russian. After a chapter page they understand the chapter almost as well as after reading the original.
- **Detailed summary, not a translation.** Keep every main idea, argument, definition, number, and warning of the chapter. Keep the order of the book. Cut repeats, side stories, and long listings.
- **Size target: 20-40% of the book chapter, aim for 30%.** Count words of the prose on the page (code blocks and their output do not count). Count words of the book chapter without code. Example: a 4,900-word chapter gives a 1,000-2,000-word page. Below 20% the page is too thin. Above 40% it is too long: cut. Count words with `python3 -I scripts/book-tools/words.py --source <chNN.txt> <page.md>`, not by eye.
- **Clear first, within the target.** If a sentence is not clear to a newcomer, add one short sentence or one small example. Do not add long explanations. Mark our own additions with `> **Пояснение:**`, at most 3 per chapter.

### Translation vs retelling

We publish on a public site, and books are copyrighted. So:

- Follow the book **section by section** and keep all its content.
- Write the sentences **in our own words**. Do not translate paragraphs word by word.
- Short quotes are fine: one sentence, in quotation marks, with "— пишет автор".
- Do not copy tables and figures. Rebuild tables in our own form. Redraw figures as our diagrams.
- Keep the note on the overview page: `> Это подробный пересказ на русском, а не перевод. За полным текстом идите в оригинал.`
- Put the EPUB link right after that note: `📥 [Скачать конспект в EPUB](/downloads/<book-slug>.epub) — для телефона и электронной книги.` See the `book-epub` skill.

Good examples to copy:
- `src/content/docs/book-summaries/engineering/data-warehouse-toolkit/` (diagrams + DuckDB practice)
- `src/content/docs/book-summaries/engineering/designing-data-intensive-applications/` (diagrams, no practice)

## Files

| What | Path |
|---|---|
| Overview | `src/content/docs/book-summaries/<group>/<book-slug>/index.md` |
| Chapter | `.../<book-slug>/NN-<chapter-slug>.md` (`01-...`, `02-...`) |
| Images | `public/assets/<book-slug>/chNN-<name>.png` |
| Diagram sources | `scripts/<book>-diagrams/` (see the `diagrams` skill) |
| Term glossary | `scripts/<book>-diagrams/glossary.md` (see "Glossary first") |
| Figure list | `scripts/<book>-diagrams/figures.md` (see "Diagrams") |
| Code from the book | `scripts/<book>-code/chNN_<name>.py` + `README.md` + `requirements.txt` |
| Cover (home page carousel thumbnail) | `public/assets/book-covers/<book-slug>.jpg` (240px wide JPEG, under 30 KB). The file name must equal the last part of the `autogenerate` directory in `src/nav.mjs`. See `references/lead.md` |
| Book text (not in git) | `<scratch>/src/chNN.txt` from `scripts/book-tools/split_source.py` |

- `<group>`: `engineering`, `business`, `entrepreneurship`, or `ai`.
- `<book-slug>`: English title in lowercase with hyphens.

## Roles and models

| Role | Who | Model, effort | Reads |
|---|---|---|---|
| Lead | Main session | `opus`, `high` | This file + `references/lead.md` |
| Chapter worker | One subagent per chapter | `opus`, `high` | This file. `references/duckdb-practice.md` only if the chapter gets DuckDB practice |
| Correctness review | Fresh subagent per chapter | `sonnet`, `medium` | `ru-proofread` skill |
| Flow pass (only if `--stats` shows `LOW`) | Fresh subagent per chapter | `opus`, `medium` | `ru-proofread` skill |

- When the lead starts an agent, it sets these models and effort levels on the Agent call.
- Do not use `haiku` for Russian text. Do not use `xhigh` or `max`: a summary is reading and writing, not hard reasoning.
- If you work alone (no workers), you are the lead. Do the chapter steps for each chapter, then the lead steps.

## Run a whole book as a workflow

For a new book (or many chapters), the lead runs two saved workflows from `.claude/workflows/` instead of starting agents by hand. They run every step in a fixed order with the models above.

| Step | Run | Result |
|---|---|---|
| 1. Prepare | `Workflow({name: "book-prep", args: {source: "<abs path to pdf/epub>", slug, group, scratch: "<abs scratch dir>", scriptsPrefix?}})` | `chNN.txt` files, word counts, `glossary.md`, `book-plan.json`, and `next.args` |
| 2. Owner check | Show the owner the chapter list (pages, words, skipped parts) and the glossary `openQuestions`. Fix the plan or glossary if needed. | Confirmed plan |
| 3. Run | `Workflow({name: "book-summary", args: <next.args from step 1>})` | All chapters written, size-checked, reviewed, flow-edited; overview, nav, cover, EPUB, build. Report with sizes and meaning risks |

- **Rerun or continue:** run step 3 again with the same args. Stages that are done have marker files in `<scratch>/state/` and are skipped. Add `"redo": true` to ignore the markers.
- **Some chapters only:** add `"only": [3, 5]`. Book steps (overview, build) are skipped in a partial run.
- **Test first:** run step 3 with `"only": [1]` and read the page before you run the whole book.
- **Record the cost** after each run: `python3 -I scripts/book-tools/token_usage.py <transcript dir of each run>`. The transcript dir is printed when the workflow starts. Add a row to "Measured cost" in `scripts/book-tools/README.md` when the numbers differ a lot.
- **Look at the result:** `npm run dev`, open the overview page, check every diagram. `npm run epub` first if you want the EPUB link to work.
- If the workflow name is not found, start a new session or pass `scriptPath: ".claude/workflows/<name>.js"`.

## Save tokens

Output tokens cost 5 times more than input tokens. Most waste comes from writing the same text twice and from reading PDF pages.

- **Read the book as text, never as PDF pages.** The lead splits the book once: `python3 -I scripts/book-tools/split_source.py <book.pdf|book.epub> <scratch>/src [--chapters "1:15-40,..."]`. A worker reads only its own `chNN.txt`. Open a PDF page as an image only to look at one figure you redraw: `pdftoppm -f N -l N -r 80 -png <book.pdf> <scratch>/fig`.
- **Write the page once, at the right size.** Get the budget per section before you start: `python3 -I scripts/book-tools/words.py --sections <scratch>/src/chNN.txt`. Plan about 30% of each section. Check the draft with `words.py --source <chNN.txt> <page.md>`. If the draft is too long, cut with `Edit`. Do not write the page again.
- **After the first `Write`, change files only with `Edit`.** Never rewrite a whole page to fix a few lines.
- **Do not read a file again right after you wrote it.** Read it again only if a script reports a problem.
- **Keep command output short.** `npm run build 2>&1 | tail -20`. Check that code is deterministic with `same_output.py` (see "Tooling"). Do not print all the output of every run.
- **Run `check.py` yourself before you hand the page on.** Fix every `ERROR`. Then the review agent has fewer edits to make.

## Chapter steps (worker)

1. **Read the whole chapter first** (`chNN.txt`). Write down its full heading tree (all H2 and H3 headings of the book).
2. **Add new terms** of the chapter to `glossary-chNN.md` (or straight to the glossary if you work alone; see below).
3. **Write the chapter page** section by section, using the translation guide. Aim for 30% of the source size.
4. **Redraw the book's figures** with the `diagrams` skill (see "Diagrams").
5. **Run and validate all code** from the chapter (see "Hands-on code from the book").
6. **Check coverage**: every heading, figure, and code example of the book chapter has a place on our page.
7. **Run the proofread script** on your page: `python3 -I scripts/ru-proofread/check.py --glossary <glossary.md> <page.md>` and `--stats`. Fix every `ERROR`. Do not start review agents: the lead runs the `ru-proofread` review and flow agents after all workers finish. The agent that wrote the chapter does not review it.
8. **Report** to the lead in a few lines: source words, page words and %, diagrams drawn and skipped, code status, doubtful places in the book. Meaning risks go in the report, not on the page.

Lead steps (cover, overview page, `nav.mjs`, EPUB, build): `references/lead.md`.

## Keep what the project already has

When you rewrite an existing page, first read the old one (`git show HEAD:<path>`). Keep our own additions:

- `## Что изменилось к 2026 году` (marked "Это наше дополнение, его нет в книге"). Copy it after `## Итоги главы`. Add bullets if needed, never remove them. Proofreading may fix the language there, but not the facts.
- The bullets in `## Что это значит на практике`. They are written for data engineers. Keep them and add new ones.
- `sidebar.order`, `sidebar.label`, file names and URLs. A renamed page needs a `redirects` entry.

## Tooling (reference: `scripts/ai-engineering-diagrams/`, `scripts/ai-engineering-code/`)

For a new book copy these files and change the paths, scene prefix and output folder:

| Tool | What it does |
|---|---|
| `excb.py` | Draws diagrams on the shared Excalidraw canvas with a lock, checks the scene and element count, waits for the frontend, exports PNG, compresses it |
| `chNN_diagrams.py` | Specs of the chapter diagrams (`N`, `E`, `Z`, `T` helpers). Run: `python3 scripts/<book>-diagrams/chNN_diagrams.py [name ...]` (not with `-I`) |
| `chNN_<name>.py` | Code of the chapter. Run with `python3 -I`, fixed seeds, same output twice |
| `embed.py` | Builds the chapter page from a template. `{{code: file.py}}` inserts the script in a `<details>` block. `{{out: file.py}}` inserts its real output. Code and output on the page always match the files |
| `figures.md`, `glossary.md`, `README.md` | Registers: figures, terms, code status |

Rules learned the hard way:

- **Look at every PNG.** Another program can draw on the shared canvas, and the export then shows foreign content. Re-run that diagram.
- Do not draw with the `excalidraw` MCP tools while a build runs.
- Arrows must not cross other boxes. Lay nodes out in rows and columns.
- A label on a short arrow hides the arrow. `excb.py` stops with "Arrow labels hide their arrows" when the gap between two boxes is too small for the label. Move the boxes apart or shorten the label. Copy `excb.py` from `scripts/data-quality-fundamentals-diagrams/`: it has this check.
- Never type script output by hand. Use `embed.py`. SQL output comes from a real `duckdb` run.
- Code must be deterministic for every Python hash seed. Never depend on the order of a `set` (use `dict.fromkeys` or `sorted`). Test each script 6 times with `python3 -I scripts/book-tools/same_output.py <script.py>` (add `--python <venv>/bin/python` if the folder has a venv). It runs with hash randomization on and prints one line: `same x6` or the first diff. Running twice can pass by luck.
- Never run regex clean-ups over a whole page: code blocks have meaningful blank lines. If you edit a page after `embed.py`, check that every code block still equals its file.
- Source text of a book in another language: read the meaning, follow the logic, and fix translation errors silently. Do NOT put translation notes ("Заметка о переводе") on the pages: the owner does not want them. Tell the lead about doubtful places in your final report instead.
- Parallel work: you write only your chapter page, your images, your scripts, and `figures-chNN.md`, `glossary-chNN.md`, `README-chNN.md`. Never edit shared files (`index.md`, `nav.mjs`, registers) and never run `npm run build`. The lead does that.

## Translation guide

### 1. Glossary first

Before chapter 1, make `scripts/<book>-diagrams/glossary.md`: a table `English | Как пишем | Не писать | Пояснение`. Add new terms for every chapter. Use the same word for the same term in all chapters. The column `Не писать` lists wrong variants (for example `склад данных`). `check.py --glossary` fails on them. Write `—` if there is none.

Technical terms stay in English. Do not translate them to be "more Russian". Make the Russian around them correct.

**One form per term.** For each term the glossary gives exactly one form: English (`consumer`) or an established Russian word (`партиция`, `кэш`, `поток`). Never both on one page. `check.py` reports a page with both forms as `term-drift`. Put the other form in `Не писать`. The owner decides the form. If the glossary has no entry for a term, keep the form the book's pages use most and ask.

| Kind of term | Rule | Example |
|---|---|---|
| Established English term in the field | Keep English in backticks. Explain in Russian at first use | `grain`, `fine-tuning`, `embedding`, `RAG` |
| Term with a common Russian word | Use Russian. Give English in brackets at first use only | оценка (evaluation), задержка (latency) |
| Name of a product, model, benchmark, paper | Keep as is, no backticks | GPT-4, MMLU, Chatbot Arena |
| Author's own new term | English in backticks + explanation | `AI as a judge` |

At first use in each chapter, write: `<term> — <простое объяснение>`. Example: "`Perplexity` — это мера того, насколько модель «удивлена» текстом. Чем она ниже, тем лучше модель предсказывает следующий токен."

### 2. Section by section

- Each H2 of the book becomes an `##` on our page. Each H3 becomes `###`. Use the book's order. You may join two very short sections.
- Headings in Russian. Keep the English term in a heading when it is the topic: `## AI as a judge: модель оценивает модель`.
- For each section, retell **all** of it:
  - the main claim;
  - the reasoning: why the author thinks so;
  - definitions;
  - examples and cases (keep them; change the wording, and the data if it is long);
  - numbers and study results that support the claim, with one line on what they show;
  - the author's advice and warnings.
- Hard parts get one clear sentence of explanation. Do not drop a main idea because it is hard. Do drop a minor example, a repeat, or a side detail to stay in the size target.

### 3. Sentences

- One idea per sentence. Split long English sentences into 2-3 Russian ones.
- Use active voice: "Модель выбирает ответ", not "Ответ выбирается моделью".
- Keep the author's voice where it matters: "Автор считает...", "Хьюен предупреждает...". This shows what is opinion and what is fact.
- Use linking words so the logic is clear: "поэтому", "но", "из-за этого", "например", "иначе говоря".
- Use full sentences in bullets, not fragments.

**Flow.** Short sentences are good. A row of short sentences with no links is not: it reads like a list of facts. Write so that each sentence follows from the one before.

- Shape of a paragraph: claim, then why, then an example or a result.
- No more than 3 short sentences in a row. Mix short ones with medium ones (10-20 words).
- In prose every sentence has a verb. No one-word sentences like "Просто." (fine in table cells).
- Join two halves of one thought with a colon, "и", "а", "но", "который".
- Known first, new last: the main word of the sentence goes to the end.
- Do not add a cause the book does not state. "Поэтому" and "потому что" are claims.
- Check: `python3 -I scripts/ru-proofread/check.py --stats <chapter.md>`. Targets: median 8+ words per sentence, 30% or less sentences of 5 words or less, 10+ link words per 100 sentences. They are a guide. Do not pad.

| Dry | Better |
|---|---|
| Автоматика удобна, но непредсказуема. Rebalancing нагружает сеть и узлы. Поэтому часто нужен человек в цикле. Couchbase и Riak предлагают план, но ждут подтверждения. | Автоматика удобна, но непредсказуема. К тому же rebalancing нагружает сеть и узлы. Поэтому в процессе часто оставляют человека: Couchbase и Riak сами предлагают план, но ждут подтверждения. |
| Новичок. Читайте по порядку. Главы 1, 2, 5 дают основу. | Новичку лучше читать по порядку: главы 1, 2 и 5 дают основу. |

More rules and examples: `.claude/skills/ru-proofread/references/rules.md`.

### 4. Common translation mistakes

The full and growing list is in `scripts/ru-proofread/calques.tsv`, and the `ru-proofread` skill checks it. Short version:

| English | Wrong | Right |
|---|---|---|
| actually | актуально | на самом деле |
| eventually | эвентуально | в итоге |
| it makes sense | это имеет смысл | это разумно / так логично |
| significant (not statistics) | сигнификантный | заметный, важный |
| to address a problem | адресовать проблему | решить проблему |
| performance (of a model) | перформанс | качество (для точности), скорость (для latency) |
| leverage | левереджить | использовать |
| it is worth noting | стоит отметить, что | (delete it, just say the fact) |

Also:
- A definition needs a dash: `Партиция — это часть данных`, not `Партиция это часть данных`.
- Every verb needs its object and the right subject. Read each sentence and ask: who does what to whom?
- Do not copy English word order. Put the main point at the start of the sentence.
- Numbers: Russian format in text (`0,85`, `10 000`), but keep `.` inside code and formulas.
- Units and money: keep the original (`$20`, `ms`), do not convert.

### 5. Make it clear

When a passage assumes knowledge the reader may not have:

- Add a short explanation in brackets or one extra sentence.
- Add an example from data engineering where it helps: an orders table, a SQL query, a pipeline.
- For a formula: write it, then explain each part in words, then give a small example with numbers.
- Mark our own additions so they are not taken as the author's words: `> **Пояснение:** ...`.

## Diagrams

**Redraw the book's figures.** Go through every figure in the chapter and redraw it as our diagram.

1. List all figures of the chapter: `Figure N-M`, what idea it shows, which section it is in.
2. Redraw every figure that shows a concept, flow, architecture, process, or comparison. Skip only screenshots, photos, and figures that add nothing to the text. Write the skipped ones and the reason in the figure list.
3. How to redraw:
   - Keep the idea: the same blocks, arrows, and relations, so the reader learns the same thing.
   - Draw it in our style with the `diagrams` skill. Our layout, colors, and shapes. Do not trace or screenshot the original.
   - All labels in Russian. Keep English terms the same as in the glossary.
   - For a chart with data (a plot of results), draw a simple chart of the trend with our own example numbers. Say in the text what the original result was.
4. Add our own diagrams where the book has none, but a flow or comparison is hard to follow in text.
5. Each chapter has at least one diagram. Keep 3-4 per chapter: the ones that carry the main ideas. Skip decorative ones (timelines, logos).

Placement:
- Put the diagram right after the paragraph that explains it. Add one sentence on how to read it.
- File name: `public/assets/<book-slug>/chNN-<name>.png`. Source in `scripts/<book>-diagrams/`.
- Keep the figure list in `scripts/<book>-diagrams/figures.md`: `Глава | Figure | Идея | Наш файл | Статус (redrawn / skipped: причина)`.
- `alt` in Russian, describing what the diagram shows.
- Use the `diagrams` skill: Excalidraw for flows and architecture, Mermaid only for ER.

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
1. `**Главная мысль:** ...` - 2-3 sentences in plain words.
2. `## О чём глава` - one paragraph: what question the chapter answers, how it links to the previous chapter (with a link), and a list of the chapter's main topics.
3. Main diagram of the chapter.
4. The chapter content: `##` / `###` sections that follow the book (see the translation guide). Other diagrams go inside the sections.
5. `## Итоги главы` - 6-10 bullets. Each is one full sentence with one idea.
   Then `## Что изменилось к 2026 году` if the old page had it (see "Keep what the project already has").
6. `## Ключевые термины` - table: Термин | Значение. Same words as in the glossary.
7. `## Что это значит на практике` - bullets for a data engineer's daily work.
8. Practice: 1-3 short code snippets of the chapter with their real output, and, for technical books, a short `## Практика в DuckDB` with 2-3 tasks (read `references/duckdb-practice.md` first). Full scripts live in `scripts/<book>-code/` and the page links to them. Do not embed whole scripts in `<details>`.
9. `## Вопросы для самопроверки` - 4-6 numbered questions. Ask "why" and "when", not only "what".
10. Last line: `Предыдущая: [..](..). Следующая: [..](..).` with root-absolute links and a trailing slash.

## Hands-on code from the book

If the chapter has code (SQL, Python, shell, config), it goes on our page, and it must run.

1. **List the code.** Write down every code example of the chapter: language, what it shows, which section.
2. **Write our version.** Show the same technique with our own code: our names, our data, our comments in Russian. Do not paste long listings from the book. Short one-line commands (`pip install x`, `duckdb`) can stay as they are.
3. **Make it self-contained.**
   - Data is generated in the code (`VALUES`, `generate_series`, a seeded random generator) or is an open dataset with a link.
   - Pin versions: `pip install pandas==2.2.3`.
   - No paid API keys needed to run the main example. If the book calls a paid API (OpenAI, Anthropic), give a local or mock version that runs for free, and show the API call as a separate, clearly marked block.
4. **Run it.**
   - SQL: `duckdb` CLI, or `python3 scripts/kimball-diagrams/check_sql.py <chapter.md>`. It must print `OK`.
   - Python: put the code in `scripts/<book>-code/chNN_<name>.py` and run `python3 scripts/<book>-code/chNN_<name>.py`. Use a venv and a `requirements.txt` in that folder.
   - Shell: run every command in a clean temp folder.
5. **Write the real output into the page.** Copy the actual output under the code block as `text`. Never invent output.
6. **Fix what does not run.** If book code is outdated (old library API), update it to the current version. Add `> **Пояснение:** в книге используется <старый API>, здесь код обновлён под <версию>.`
7. **Keep the code list** in `scripts/<book>-code/README.md`: `Глава | Пример | Файл | Статус (ok / не запускается: причина)`. Every row must be `ok` before commit, or have a clear reason (for example, it needs a GPU).

## Format rules

- No `#` headings in the body. Start at `##`.
- Tables are for comparisons and lists of variants. Explain the idea in text before the table.
- Code-like terms in backticks: `grain`, `surrogate key`, `SCD2`.

## Check before you finish

For each chapter, answer yes to all:

- [ ] Every H2/H3 of the book chapter has a section on our page (very short ones may be joined).
- [ ] Prose size is 20-40% of the book chapter: `words.py --source <chNN.txt> <page.md>` prints `ok`. Report both numbers.
- [ ] Every main definition, argument, number, and warning of the chapter is there.
- [ ] Every term is explained at first use, with the same word as in the glossary.
- [ ] Hard passages have one clear sentence of explanation.
- [ ] No paragraph is a word-by-word translation. No copied tables or figures.
- [ ] `python3 -I scripts/ru-proofread/check.py <chapter.md>` shows no `ERROR`. Every `WARN` is fixed or judged fine. Meaning risks are in the report.
- [ ] Lead only, after the review and flow agents: `check.py --before <old version> <chapter.md>` passes, so code, links and numbers are unchanged by proofreading.
- [ ] `check.py --stats <chapter.md>` is `ok`, or you can say why the page stays below the targets.
- [ ] Every figure of the book is redrawn or listed as skipped with a reason in `figures.md`. 3-4 diagrams stay on the page.
- [ ] Every code example runs. The output on the page is the real output. `scripts/<book>-code/README.md` is all `ok`.
- [ ] A reader who has not read the book understands the page without the original.
