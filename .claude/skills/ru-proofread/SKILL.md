---
name: ru-proofread
description: Proofread Russian text on dataengineer.ru so it reads clearly and pleasantly - fixes calques from English, missing dashes, wrong or missing objects, choppy flow and typography, and keeps technical terms in English. Use after writing or editing any Russian page (book summary, practice lesson, article), when the user asks to вычитать, проверить русский, улучшить текст, fix calques, improve flow, or when Russian text sounds like a translation.
---

# Russian proofreading (вычитка)

Goal: the page reads like it was written in Russian, not translated. The reader should feel no friction.

There are three different jobs. Do all of them.

| Job | What it fixes | Who does it |
|---|---|---|
| Correctness | Dashes, calques, broken sentences, wrong terms, typography | Script + correctness review |
| Flow | Choppy rhythm, no links between sentences, telegraphic fragments | Flow pass |
| Clarity | Vague or empty sentences, AI slop, unclear «это», contradictions inside the page | Clarity pass |

Technical terms stay in English (`grain`, `hot spot`, `scatter/gather`). We do not translate them. We only make the Russian around them correct and smooth.

Guide for humans, with test results: `scripts/ru-proofread/README.md`.

## When to run

- After you finish a chapter or page, before `npm run build` and before commit.
- On any page the user calls "rough", "like a translation", "dry", or "silly mistakes".
- The agent that wrote the text does not review it. With parallel chapter workers, the **lead** starts the review agents after the workers finish.
- Many site pages at once (not book summaries): run the saved workflow `page-proofread` (`.claude/workflows/page-proofread.js`). Group the pages into batches of 2,000–4,000 Russian words. Each batch gets steps 2, 4 and 5. Then do steps 3 and 6 yourself: guard, diff, `check.py`, `npm run build`. Agents do not touch front matter, so fix titles yourself.

## The pipeline (6 steps, in this order)

Keep a copy of the page before you start: `cp <page>.md <scratch>/before.md`.

### Step 1. Script

```bash
python3 -I scripts/ru-proofread/check.py --fix <page.md>          # quotes and number ranges only
python3 -I scripts/ru-proofread/check.py --glossary scripts/<book>-diagrams/glossary.md <page.md>
python3 -I scripts/ru-proofread/check.py --stats <page.md>        # rhythm numbers
```

- It checks prose only. It skips front matter, code, inline code, links.
- `--fix` changes only `"…"` to `«…»` and `00-99` to `00–99`. It skips headings, code and risky lines.
- `ERROR` must be fixed. `WARN` is a question: fix it or decide it is fine.
- Silence a false positive: put `<!-- ru-proofread:ignore-line -->` on the line before it.
- `term-drift` means the page uses two forms of one term (`потребитель` and `consumer`). Pick the form from the book glossary. If the glossary does not say, ask the owner and write the answer into the glossary.
- Lecture glossaries have the line `<!-- ru-proofread: two-languages -->`. Then `first-mention` means the first paragraph with a term lacks its second language (write the glossary form «токенизация (`tokenization`)»), and `term-lead` means the English form of a Russian-led term comes back later (use the Russian word).

### Step 2. Correctness review (fresh agent)

Prompt: `references/review-prompt.md`. Give the agent the page, `references/rules.md`, the glossary, and the output of step 1.

Model: `sonnet`, effort `medium`. It does two passes: meaning (who does what to whom), then terms, calques and punctuation. It fixes the page in place with small `Edit` calls. It writes no full copy and no change log. It replies with counts per type and a list of **meaning risks**.

### Step 3. Guard

```bash
python3 -I scripts/ru-proofread/check.py --before <scratch>/before.md <page.md>
```

Code blocks, inline code, links, numbers, headings and front matter must be the same. Length may change by 5%. Fix every `ERROR` before you go on.

### Step 4. Flow pass (fresh agent)

Run it when `--stats` shows `LOW` or the script reports `choppy`. Otherwise skip it. Prompt: `references/flow-prompt.md`. Model: `opus`, effort `medium`. It edits paragraphs in place, with no change log.

- It works on paragraphs, not on single words. It links sentences and fixes the rhythm.
- It adds no facts and no new cause-and-effect claims.
- Length may grow by up to 10%. The page must stay inside the size target of the `book-summary` skill.
- Then run the guard again: `check.py --before <scratch>/before.md --max-change 10 <page.md>`.

Targets for `--stats` (from our best-reading summary, Data Warehouse Toolkit):

| Number | Target |
|---|---|
| Median words per sentence | 8 or more |
| Sentences of 5 words or less | 30% or less |
| Link words per 100 sentences | 10 or more |

The numbers are a guide, not a goal. Do not pad sentences to hit them.

### Step 5. Clarity pass (fresh agent, always)

Prompt: `references/clarity-prompt.md`. Model: `opus`, effort `high`. It always runs, because `--stats` cannot see vague text. It reads the whole page as a newcomer and checks meaning against the source.

- It fixes empty sentences, AI slop and filler, slang, unclear references, contradictions, and promises that do not match the content («в два шага», then four steps).
- It may delete up to 3 low-value sentences. It never deletes a definition, number, warning or argument.
- It must fix the places the writer or the review flagged as unclear.
- It replies with `New patterns`. Add the repeatable ones to `scripts/ru-proofread/calques.tsv`.
- Then run the guard: `check.py --before <scratch>/before.md --max-change 10 <page.md>`.

Why: on the first book with this pipeline (Analytics Engineering with SQL and dbt) the review made 1-2 edits per chapter, and the flow pass never ran. A human read of chapter 1 still found 8 unclear sentences.

### Step 6. Re-run and report

1. Run step 1 again. No `ERROR` is left.
2. Build the compare page for the owner when they ask for it: `python3 -I scripts/ru-proofread/compare.py <scratch>/before.md <page.md> <scratch>/compare.html "Title"`. The diff comes from the two files, so no change log is needed.
3. Put **meaning risks** in your final report, not on the page. The owner does not want translation notes on pages.

## What counts as a meaning risk

Report these to the lead, do not decide alone:

- the fix changes what a sentence claims (for example `общая задача` → `частный случай задачи`);
- a link word would state a cause that the text does not state;
- an unclear passage where you cannot tell what the book says;
- a number, name, or term that looks wrong.

If the original book is not in front of you, say so.

## Rules in short (full list in `references/rules.md`)

1. Definition `X — это Y` needs a dash. Not `X это Y`.
2. Every verb has its object and the right subject. Not "он путает", not "чтение должно читать".
3. No calques. Not "имеет смысл", "человек в цикле", "справедливо распределена", "лечат проблему".
4. Do not translate technical terms. Do translate the words around them. One form per term on a page.
5. Link the sentences and vary the rhythm. No more than 3 short sentences in a row.
6. Typography: «ёлочки», `—` as dash, `–` in ranges, `0,85` in text.

## Grow the rules

Each time you find a silly mistake, add it:

- a repeatable phrase → one line in `scripts/ru-proofread/calques.tsv`;
- a repeatable pattern → one example in `references/rules.md`;
- a wrong term → `Не писать` column in the book glossary;
- two forms of one term → one line in `scripts/ru-proofread/term-pairs.tsv`;
- a changed regex or a new rule → one case in `scripts/ru-proofread/test_check.py`. Run it.

Do not add vague rules. Add examples from real pages.
