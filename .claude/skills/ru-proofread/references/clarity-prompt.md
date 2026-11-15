# Prompt for the clarity pass (final read)

The last pass. Run it after the correctness review (and the flow pass, if it ran). It always runs: `--stats` cannot see vague or empty text. Send it to a fresh subagent (`general-purpose`, model `opus`, effort `high`). The agent edits the page in place, so keep `before.md` from the start of the pipeline.

Why it exists: the correctness review fixes single lines and may not remove or change claims. The flow pass fixes rhythm. Neither asks "does this sentence say anything?" or "does this page contradict itself?". This pass does.

---

You are the final editor of a Russian page on dataengineer.ru, a site for data engineers. You did not write it. Other editors already fixed grammar, punctuation and terms. Your job: the page must be clear to a reader who has not read the book, and it must not read like AI text.

File: `<path to page>`
Book chapter (source text, to check meaning): `<path to chNN.txt>`
Glossary: `<path to glossary.md>`
Rules: `.claude/skills/ru-proofread/references/rules.md`
Places the writer flagged as unclear (fix each one or say why it is fine): `<list or "none">`

Work in two steps.

**Step 1. Find.** Read the whole page, paragraph by paragraph, as a newcomer. Stop at every sentence and ask:
- Can I say in my own words exactly what this sentence claims? If I can only guess, it is a problem.
- Would a newcomer stop and read it twice?
- Does each word mean in Russian what the author meant in English?
- Does it agree with what the page says elsewhere?

A sentence can be correct Russian and still be a problem: loose, vague, or empty. These are exactly what earlier editors missed. Prose next to code blocks counts too (the lines that explain code before and after it). Write the list of problem lines for yourself before you edit. A normal page of 2,000-5,000 words has 5-15 of them.

**Step 2. Fix** every line on your list. Problem types:

| # | Problem | Example (bad → good) |
|---|---|---|
| 1 | **Empty or vague sentence**: says nothing concrete, or the reader cannot tell what it claims | «Технологии сильно изменились.» → say what changed, from the book, or delete |
| 2 | **AI slop and filler**: stock phrases, bureaucratic words, empty adjectives | «играет ключевую роль», «в современном мире», «является неотъемлемой частью», «данный подход», «важно понимать, что», «широкий спектр» → plain words or delete |
| 3 | **Slang, jargon or calque missed by the script** | «закрыть боль», «зашипить», «релевантный» (= подходящий), «имплементировать» → normal Russian |
| 4 | **Unclear reference**: «это», «такой», «общий», «он» with no clear antecedent | «Он хранит их отдельно.» after two nouns → «Брокер хранит партиции отдельно.» |
| 5 | **Contradiction inside the page**: two places say different things about one fact. If the book itself says both, use a wording that is true for both places | «слоёв три» in one section, a list of four layers in another → check the book, make them match |
| 6 | **Low-value sentence that confuses**: a minor detail the reader cannot understand without more context | delete it, if the section stays complete without it. Deleting is better than leaving a sentence nobody understands |
| 7 | **Word that means something else in Russian** | «адекватный» for adequate, «утилизировать» for utilize, «драматически» for dramatically → the right word |
| 8 | **Loose comparison or link**: «как X», «так же, как Y», «по сути» where the reader cannot tell what is compared | «Это работает как конвейер.» → say what exactly is the same |
| 9 | **Promise and content do not match**: «в два шага», then four steps; «три причины», then two | fix the number or the text |

Hard limits:
- Check every change against the book chapter. Do not add facts the book does not have. Do not change numbers, names, code, links, image paths, headings or front matter.
- You may delete at most 3 sentences. Only types 1, 2 and 6. Never delete a definition, a number, a warning or an argument of the author.
- English technical terms stay as in the glossary.
- Do not touch code blocks and their output, the key terms table, the self-check questions, the navigation line at the end.
- Do not redo the rhythm of good paragraphs. Do not touch a sentence that passes all four questions of step 1.
- **Clarity beats brevity.** If a sentence needs a few more words, or one more sentence from the book, to be clear, add them. The page may grow by up to 15%.
- If a fix may change what the author claims, do not apply it. List it under "Meaning risks".

How to edit:
- `Edit` in place, one sentence per edit. Never `Write` the whole file. Keep the same number of lines and the same line order.
- Do not read the page again after your edits. Do not write a change log.

Reply with only:
1. `Found`: every problem line from step 1, one per line: `line N, type T: problem → fixed` or `→ left: why`.
2. The number of changes per problem type (1-9).
3. `Meaning risks`: line, text, why.
4. `New patterns`: words or phrases that will repeat in other pages and a script could catch (for `calques.tsv`). One per line: `bad → good`. Empty if none.

---

Notes for the lead:
- After the pass run the guard: `check.py --before <before.md> --max-change 20 <page.md>`, and `check.py --glossary <glossary> <page.md>`.
- Read the diff (`diff <before.md> <page.md>`). Check every deleted sentence against the book.
- Add good `New patterns` to `scripts/ru-proofread/calques.tsv`, so the script catches them next time.
