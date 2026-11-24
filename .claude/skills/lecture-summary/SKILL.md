---
name: lecture-summary
description: Write a Russian summary of a university lecture course from YouTube (конспект курса лекций) for dataengineer.ru - download the transcripts, then one overview page per course plus one teaching page per lecture, with Excalidraw diagrams, runnable examples and self-check questions, under src/content/docs/lecture-summaries/. Use when the user asks to summarize YouTube lectures or a course (Stanford CS336, CME295, CS229, Harvard CS50, CMU 15-445 and similar), to download YouTube transcripts, to add a course or lecture to "Конспекты лекций", or to fix an existing lecture summary.
---

# Lecture summary (конспект курса)

A lecture summary is a Russian retelling of a university course from YouTube. It is a folder with an overview page and one page per lecture. The source is the transcript of each video, plus the course slides and notes when they exist.

It works like the `book-summary` skill. This file covers what is different. For the shared rules, read these sections of `.claude/skills/book-summary/SKILL.md`: "Translation guide" (all 5 parts), "Tooling", "Hands-on code from the book", "Format rules". Read "book" there as "lecture". For terms, "Terms in two languages" below replaces the table "Kind of term" of the book guide.

## The goal

- **Reader:** a Russian-speaking data engineer who has NOT watched the lecture and may not know the field.
- **Goal: learn the fundamentals.** After a lecture page the reader understands the main ideas of the lecture: what they are, why they matter, and how they work. The page teaches. It does not only list what the lecturer said.
- **Detailed summary, not a transcript.** Keep every main idea, definition, argument, number, example and warning. Keep the lecture's order. Cut filler, jokes, repeats, logistics and pauses in live coding.
- **Size target: 30-40% of the transcript, aim for 35%.** These courses teach fundamentals, so quality beats a short page (the owner's decision, 2026-11-24; it was 15-25%). Use the room to explain: each main concept gets what it is, why it is needed, how it works, and an example or a small calculation. Do not use it for filler, jokes or repeats of the lecturer. A 75-minute lecture has about 11,000 words, so its page has 3,300-4,400 words. Count with `python3 -I scripts/book-tools/words.py --target 30-40 --source <lecNN.md> <page.md>`, not by eye.
- **Clear first.** Clarity beats brevity. The clarity pass may take the page up to 45%.

### Teach, not just retell

For each main concept of the lecture, the page answers five questions, in this order:

| Question | Example: BPE tokenization |
|---|---|
| What is it? One sentence | `BPE` — это способ построить словарь токенов из частых пар символов |
| Why is it needed? | Словарь из целых слов слишком большой, а из букв даёт слишком длинные последовательности |
| How does it work? Steps | Начинаем с байтов, считаем пары, сливаем самую частую пару в новый токен, повторяем |
| A small example with numbers or code | `"low lower lowest"` → три шага слияния, с реальным выводом скрипта |
| Where do people get it wrong? | Токен — не слово: одно редкое слово может занять 4 токена |

- Build intuition before the formula. Say the idea in words, give the formula, explain each symbol, then show a small example with numbers.
- Link a new idea to what a data engineer knows: a table, a SQL query, a pipeline, a hash, an index. Mark such links as our own: `> **Пояснение:** ...`, at most 4 per lecture.
- The reader cannot see the slides. When the lecturer says "as you can see here", write what the slide shows (from the slides text) or draw it as our diagram.

### Terms in two languages

The reader learns each term in Russian and in English: Russian to understand it, English to read papers, docs and code. So the first mention of a term on a page shows both languages.

| Case | First mention | Later on the page |
|---|---|---|
| Russian ML texts have a common Russian word | токенизация (`tokenization`), скрытое состояние (`hidden state`), дообучение (`fine-tuning`) | токенизация |
| No good Russian word, or it is long, clumsy or a transliteration («эмбеддинг», «промпт») | `embedding` (векторное представление), `softmax` (функция, которая превращает числа в веса с суммой 1) | `embedding` |
| An abbreviation | `LLM` (большая языковая модель), `RL` (обучение с подкреплением) | `LLM` |
| A name of a model, method, paper or dataset | Word2vec, FlashAttention, BERT | as is |

- The glossary decides the case for each term: its column «Как пишем» is the first-mention form. Read it before you write. A new term goes to `glossary-lecNN.md` in the same form.
- "First mention" means the first paragraph, list item or table cell with the term. Headings do not count. You may repeat both languages later, at the definition, if it helps the reader.
- Headings and diagram labels use the leading form only, without brackets.
- The table `## Ключевые термины` shows both languages: Термин | English | Значение.
- The course glossary has the line `<!-- ru-proofread: two-languages -->`. With it, `check.py --glossary` warns `first-mention` when a first mention has one language only, and `term-lead` when the English form of a term where Russian leads comes back outside brackets.

### Spoken source: what is different from a book

| In the transcript | What we do |
|---|---|
| Filler, jokes, "can everyone hear me?", repeats | Drop |
| Logistics: grading, homework, deadlines, office hours, staff | Drop from lecture pages. The overview page gets 2-3 sentences on how the course works |
| A student question with a useful answer | Keep it in its section: `**Вопрос из зала:** ... Ответ лектора: ...`. At most 3 per lecture |
| An error of automatic captions ("cooda" for CUDA, "CS 33336" for CS 336) | Fix it silently from the context and the slides. List doubtful ones in your report |
| "This", "here", "this one" pointing at a slide or the board | Say what it points at. Use the slides text |
| Live coding | Our own small runnable version (see "Code and practice"). Never copy a long listing |
| A story or joke that carries an idea | Keep the idea in one sentence. Drop the story |
| A side topic the lecturer calls "just for fun" or "not on the exam" | Keep only if it helps a main idea |

### Copyright

Lectures are copyrighted like books. Some courses (CS50) use CC BY-NC-SA: we still retell, and we credit. So:

- Retell in our own words. No word-by-word translation. A short quote is fine: one sentence in «ёлочках» with «— говорит лектор» or the name.
- Do not copy slides, figures or tables. Rebuild tables in our own form. Redraw figures as our diagrams.
- Credit the course: every lecture page links to its video, and the overview page names the university, the lecturers and the course site.
- Keep this note on the overview page: `> Это подробный пересказ лекций на русском, а не перевод. Видео, слайды и задания — на сайте курса.`

## Files

| What | Path |
|---|---|
| Overview | `src/content/docs/lecture-summaries/<group>/<course-slug>/index.md` |
| Lecture | `.../<course-slug>/NN-<lecture-slug>.md` (`NN` = the course's own lecture number: `00-...` for CS50, `01-...` for most) |
| Images | `public/assets/<course-slug>/lecNN-<name>.png` |
| Diagram sources | `scripts/<prefix>-diagrams/` (`excb.py`, `lecNN_diagrams.py`) |
| Term glossary | `scripts/<prefix>-diagrams/glossary.md`, with the line `<!-- ru-proofread: two-languages -->` (see "Terms in two languages") |
| Figure list | `scripts/<prefix>-diagrams/figures.md` |
| Code and practice | `scripts/<prefix>-code/lecNN_<name>.py` + `README.md` + `requirements.txt` |
| Transcript (not in git) | `<scratch>/src/lecMM.md` and `lecMM.json` from `fetch_transcripts.py` (`MM` = position in the playlist) |
| Slides and notes as text (not in git) | `<scratch>/materials/lecNN.txt` |
| Status of every course | `scripts/lecture-tools/status.md` |
| Courses we plan next, with playlists and cost | `TODO.md` in the repo root |

- `<group>`: `ai` (LLM, ML), `cs` (programming, algorithms, systems), `data` (databases, data systems).
- `<course-slug>`: school and course code, lowercase with hyphens: `stanford-cs336`, `stanford-cme295`, `harvard-cs50-sql`, `cmu-15-445`. Add the year only if we summarize two editions of one course.
- `<prefix>`: the course slug or a short form (`cs336`).
- No cover file: the home page carousel shows books only. The EPUB draws its own cover.

## Transcripts from YouTube

`scripts/lecture-tools/fetch_transcripts.py` downloads the captions of a playlist or of single videos. It needs `uv` and `deno` (`brew install uv deno`). Details and troubleshooting: `scripts/lecture-tools/README.md`.

```bash
uv run scripts/lecture-tools/fetch_transcripts.py "<playlist URL>" --out <scratch>/src [--only 1-3]
```

- Each video gives `lecMM.md`. YouTube chapters become `## <chapter> [mm:ss]` headings. Paragraphs start with `[mm:ss]`. Use these times for the video links on the page.
- `captions: manual` is a human transcript. `auto` is speech recognition: names, numbers and terms may be wrong. Check them against the slides.
- `index.json` lists every video of the playlist. Not every video is a lecture. Guest lectures are lectures. Trailers, announcements and recorded office hours are not.
- The transcript is the main source. Slides and notes (`materials/lecNN.txt`) show what was on the screen: formulas, tables, code, figures.

## Roles and models

| Role | Who | Model, effort |
|---|---|---|
| Lead | Main session | `opus`, `high` |
| Lecture writer | One subagent per lecture | `sonnet`, `high` |
| Correctness review | Fresh subagent per lecture | `sonnet`, `medium` |
| Flow pass (only if `--stats` shows `LOW`) | Fresh subagent per lecture | `opus`, `medium` |
| Clarity pass (always, last) | Fresh subagent per lecture | `opus`, `medium` |

The same rules as for books: never `haiku` for Russian text, never `xhigh` or `max`. The agent that wrote a page does not review it.

## Run a whole course as a workflow

| Step | Run | Result |
|---|---|---|
| 1. Prepare | `Workflow({name: "lecture-prep", args: {playlist: "<URL>", slug, group, scratch: "<abs scratch dir>", only?: "1-5", site?: "<course site URL>"}})` | Transcripts, slides as text, word counts, `glossary.md`, `excb.py` for the course, `course-plan.json`, and `next.args` |
| 2. Owner check | Show the owner: the lecture list (minutes, words, captions kind), skipped videos, materials found, glossary `openQuestions`, `practice` kind | Confirmed plan |
| 3. Run | `Workflow({name: "lecture-summary", args: <next.args from step 1>})` | All lectures written, size-checked, reviewed, flow-edited, clarity-edited; overview, nav, EPUB, build. Report with sizes and meaning risks |

- `videos: ["<URL or ID>", ...]` instead of `playlist` takes single videos, in your order.
- **Test first:** run step 3 with `"only": [2]` and read the page. Lecture 1 is often mostly logistics, so it is a poor test.
- **Publish lectures one by one:** add `"publish": true` to a run with `only`. The Course and Build steps then run too: the overview lists every lecture of the course, links the written ones and marks the others «скоро». Links between lectures point only to written pages. The next run with `publish` adds the missing «Следующая» links.
- **Rerun, some lectures only, review only, models:** the same options as `book-summary`: `"redo": true`, `"only": [3, 5]`, `"reviewOnly": true`, `"checkCode": true`, `"codeRunner"`, `"fullReport": true`, `"models": {"write": "opus/high"}`, `"notes"`, `"courseNotes"`. Model keys: `status`, `write`, `diagrams`, `size`, `review`, `flow`, `clarity`, `codecheck`, `code`, `registers`, `course`, `build`.
- **Code check:** with `checkCode`, the script `scripts/book-tools/check_code.py` runs every python and SQL block and compares the outputs with the page. An agent starts only for the blocks it flags. The runner is `codeRunner` (a venv python or a Docker wrapper), or by default a shared venv `<scratch>/venv-code` made from `requirements.txt`. Set up the environment before the test lecture. Stage markers are `<scratch>/state/lecNN.<stage>.done`.
- `only` means different things: in `lecture-prep` it is a string of playlist positions (`"1-5,8"`), in `lecture-summary` a list of lecture numbers (`[3, 5]`).
- **Status file:** every run updates the course's row in `scripts/lecture-tools/status.md`. Add the PR number: `python3 -I scripts/book-tools/status.py <slug> --kind lecture --pr "#N"`.
- **Cost** (measured on CME295 lecture 1): about $2.30 per lecture (write, review, clarity), plus about $1.50 for the Course step of each run and $0.80 for the prep. So write several lectures in one run. Numbers: `scripts/lecture-tools/README.md`.
- If the workflow name is not found, start a new session or pass `scriptPath: ".claude/workflows/<name>.js"`.

## Lecture steps (writer)

1. **Read the whole transcript first** (`lecMM.md`), then the slides text if there is one. Write down the topic tree: the YouTube chapters, plus topic changes inside long chapters.
2. **Plan the sections.** One `##` per main topic, usually one per YouTube chapter. Join tiny chapters. Split a long chapter that has two topics. Get the word budget: `python3 -I scripts/book-tools/words.py --target 30-40 --sections <lecMM.md>`.
3. **Add new terms** of the lecture to `glossary-lecNN.md`.
4. **Write the page** with one `Write`, in the format below. Apply "Teach, not just retell" to each main concept. Then change it only with `Edit`.
5. **Draw 2-4 diagrams** (see "Diagrams"). In the workflow, write the specs to `lecNN_diagrams.py` only and do not draw: the Diagrams stage, a fresh agent with a small context, draws them, looks at them on one contact sheet and fixes them. Working alone, draw them yourself.
6. **Code and practice** (see below). Every code block runs, and its output on the page is real.
7. **Check coverage:** every chapter and main topic of the lecture has a place on the page. Logistics do not.
8. **Size and script:** `words.py --target 30-40 --source <lecMM.md> <page.md>`. Over 40%: cut with `Edit` to 37% or less. Under 30%: add the missing explanations from the transcript. Then `python3 -I scripts/ru-proofread/check.py --glossary <glossary.md> <page.md>` and `--stats`. Fix every `ERROR`.
9. **Report** to the lead in a few lines: transcript words, page words and %, diagrams drawn and skipped, code status, doubtful places (unclear audio, caption errors you were not sure about, places where the slide is needed and missing).

## Lecture page

Front matter:

```yaml
---
title: "<Course code>, лекция N: <Тема по-русски>"
head:
  - tag: title
    content: "<Тема простыми словами>: лекция <Course code> | Инжиниринг Данных"   # max 70 chars
description: "Конспект лекции N курса <Course code> (<University>) на русском: <3-5 ключевых тем через запятую>."
sidebar:
  order: N
  label: "N. <Короткое название>"
tags:
  - lectures
  - <topic>
---
```

Body, in this order:

1. `**Главная мысль:** ...` - 2-3 sentences in plain words.
2. Source line: `🎬 [Видео лекции](https://www.youtube.com/watch?v=<id>) (1 ч 19 мин) · [Слайды](<url>) · Лектор: <Name>`. Leave out the slides link if there are none.
3. `## О чём лекция` - one paragraph: what question the lecture answers, how it links to the previous lecture (with a link), and a list of its main topics.
4. Main diagram of the lecture.
5. The lecture content: `##` / `###` sections in the lecture's order. The first line under each `##` is a link to that moment of the video: `▶ [12:34](https://youtu.be/<id>?t=754)`. The seconds come from the `[mm:ss]` mark in the transcript (`12:34` = 754 s). Other diagrams go inside the sections.
6. `## Итоги лекции` - 6-10 bullets. Each is one full sentence with one idea.
7. `## Ключевые термины` - table: Термин | English | Значение. Same forms as in the glossary: the leading form in «Термин», the English term in «English».
8. `## Что это значит на практике` - bullets for a data engineer's daily work.
9. `## Практика` - only if the course has practice (see below).
10. `## Вопросы для самопроверки` - 4-6 numbered questions. Ask "why" and "when", not only "what". Put a short answer (1-3 sentences) under each question in `<details><summary>Ответ</summary> ... </details>`.
11. Last line: `Предыдущая: [..](..). Следующая: [..](..).` with root-absolute links and a trailing slash. The first lecture links to the overview page.

## Diagrams

The lecture's slides and board drawings are its figures. Use the `diagrams` skill (Excalidraw for flows and architecture, Mermaid only for ER) and the "Diagrams" rules of `book-summary`.

1. Find the visual moments: slides the lecturer explains for a while, board drawings, "let me draw this", a mechanism with steps (a training loop, attention, a query plan).
2. Draw 2-4 diagrams per lecture: the main one (the map of the lecture's idea) and one per hard mechanism. Our layout, colors and Russian labels: each term in its leading form from the glossary. Never trace or screenshot a slide.
3. A chart of results (a loss curve, a scaling law): draw a simple chart of the trend with our own example numbers, and say in the text what the real result was.
4. Each diagram goes right after the paragraph that explains it, with one sentence on how to read it. `alt` in Russian.
5. Specs: `scripts/<prefix>-diagrams/lecNN_diagrams.py` with the `N`, `E`, `Z`, `T` helpers of `excb.py`. Run: `python3 scripts/<prefix>-diagrams/lecNN_diagrams.py [name ...]`. Look at every PNG: put them on one sheet with `node scripts/book-tools/contact_sheet.mjs <out.png> public/assets/<course-slug>/lecNN-*.png` and read it once.
6. Keep the figure list `figures-lecNN.md`: `Лекция | Что на слайде | Идея | Наш файл | Статус (redrawn / own / skipped: причина)`.

## Code and practice

- **Code from the lecture.** If the lecturer shows code (live coding, a notebook, an "executable lecture"), write our own short version that shows the same idea: `scripts/<prefix>-code/lecNN_<name>.py`, our names, our data, comments in Russian. Python with the standard library or `numpy`. Pin versions in `requirements.txt`. No GPU, no paid API keys, no large model downloads. If the idea needs a GPU or a big model, show a tiny version that runs on a laptop and say so.
- **Real output only.** Run the script, paste its real output under the code as `text`. Check it is the same on every run: `python3 -I scripts/book-tools/same_output.py <script.py>`.
- **Check the page against the files:** `python3 -I scripts/lecture-tools/check_code.py <page.md> scripts/<prefix>-code --prefix lecNN --python <venv>/bin/python` prints `ok` for every file. Run it again after any edit of a code block.
- You may build the page from a template with an embed script, but do not commit that script: its template stays in the scratchpad, and after proofreading the page itself is the source.
- **Practice** (the `practice` value of the course plan):

| `practice` | Courses | `## Практика` |
|---|---|---|
| `python` | Programming, ML, LLM (CS336, CME295, CS50 Python) | 2-3 small tasks in Python. Each solution is a file `lecNN_task<k>.py`, shown in `<details><summary>Решение</summary>` with its real output |
| `duckdb` | Databases and SQL (CS50 SQL, CMU 15-445) | 2-3 SQL tasks. Follow `.claude/skills/book-summary/references/duckdb-practice.md`. Check: `python3 scripts/kimball-diagrams/check_sql.py <page.md>` prints `OK` |
| `none` | Theory, talks, management | No `## Практика` section |

- A task trains the lecture's main idea, not a side detail. Give the expected result in the task text so the reader can check themselves.
- Keep the code list in `scripts/<prefix>-code/README-lecNN.md`: `Лекция | Пример | Файл | Статус (ok / не запускается: причина)`.

## Keep what the project already has

When you rewrite an existing lecture page, read the old one first (`git show HEAD:<path>`). Keep our own additions, `sidebar.order`, `sidebar.label`, file names and URLs, as the same section of `book-summary` says.

## Check before you finish

For each lecture, answer yes to all:

- [ ] Every chapter and main topic of the lecture has a section on the page. Logistics are not there.
- [ ] Prose size is 30-40% of the transcript: `words.py --target 30-40 --source <lecMM.md> <page.md>` prints `ok`.
- [ ] Every main concept answers: what, why, how, an example, a common mistake.
- [ ] Every main definition, argument, number and warning of the lecture is there.
- [ ] Every `##` of the lecture content starts with a `▶ [mm:ss](https://youtu.be/<id>?t=<s>)` link, and the time matches the transcript.
- [ ] Every term is explained at first use and shows both languages there, in the glossary form. `check.py --glossary` shows no `first-mention` or `term-lead`.
- [ ] No paragraph is a word-by-word translation. No copied slides, tables or figures.
- [ ] 2-4 diagrams, each right after its paragraph, `alt` in Russian. You looked at every PNG.
- [ ] Every code block runs, its output is real (`check_code.py` is all `ok`), and `README-lecNN.md` is all `ok`.
- [ ] Every self-check question has a short answer in `<details>`.
- [ ] `python3 -I scripts/ru-proofread/check.py <page.md>` shows no `ERROR`.
- [ ] A reader who has not watched the lecture understands the page without the video.

Lead steps (overview page, nav, the first course and the «Конспекты лекций» tab, EPUB, build): `references/lead.md`.
