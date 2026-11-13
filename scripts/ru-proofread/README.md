# ru-proofread: how it works

Tools and rules to make our Russian text read like Russian, not like a translation.

- Technical terms stay in English (`hot spot`, `grain`, `scatter/gather`). We do not translate them.
- We fix the Russian around them. There are two jobs:
  - **Correctness:** calques, missing dashes, broken sentences, wrong terms, typography.
  - **Flow:** choppy rhythm, no links between sentences, telegraphic fragments.
- The skill is in `.claude/skills/ru-proofread/`. This folder has the scripts and data.

## The pipeline

| Step | Who | What |
|---|---|---|
| 1. Script | `check.py` | Fixed patterns. `--fix` repairs quotes and number ranges |
| 2. Correctness review | Fresh agent | Meaning, grammar, terms, calques, punctuation |
| 3. Guard | `check.py --before` | Code, links, numbers, headings did not change |
| 4. Flow pass | Fresh agent | Links between sentences, rhythm, fragments |
| 5. Re-run and compare | `check.py`, `compare.py` | No errors left. Before/after page for the owner |

The agent that wrote the text never reviews it.

## Why these steps

One tool is not enough. We tested on DDIA ch 6 and Airflow ch 4.

| Tool | What it found | Verdict |
|---|---|---|
| LanguageTool (local) | Almost nothing real. Flags `партиционирование` as a typo | Not used |
| `typograf` | Breaks Markdown (`- ` bullets, `**bold:**`) | Not used |
| `check.py` | Fixed patterns. Findings were real | Step 1 |
| Correctness review | Broken sentences, wrong subjects, wrong terms. About 2/3 of all fixes | Step 2 |
| Flow pass | The correctness review made only 2 flow changes out of 33. Flow needs its own pass | Step 4 |

## Folder

| File | What it does |
|---|---|
| `check.py` | Checks, rhythm stats, guard, safe fix. Standard library only |
| `calques.tsv` | Calques and stop words. One line per rule |
| `term-pairs.tsv` | Russian and English forms of one term (`потребитель` / `consumer`) |
| `test_check.py` | Tests for `check.py`. Run after every change |
| `compare.py` | Builds a before/after HTML page |

Rules and prompts: `.claude/skills/ru-proofread/references/` (`rules.md`, `review-prompt.md`, `flow-prompt.md`).

## Quick start

```bash
cp <page>.md /tmp/before.md

# Step 1: script
python3 -I scripts/ru-proofread/check.py --fix <page>.md
python3 -I scripts/ru-proofread/check.py --glossary scripts/<book>-diagrams/glossary.md <page>.md
python3 -I scripts/ru-proofread/check.py --stats <page>.md

# Steps 2 and 4: ask Claude
#   "Use ru-proofread on <page>"   (it starts the review agent, then the flow agent)

# Step 3 (after each agent): guard
python3 -I scripts/ru-proofread/check.py --before /tmp/before.md <page>.md
python3 -I scripts/ru-proofread/check.py --before /tmp/before.md --max-change 10 <page>.md   # after the flow pass

# Step 5: compare
python3 -I scripts/ru-proofread/compare.py /tmp/before.md <page>.md changes.md /tmp/compare.html "Title"
open /tmp/compare.html
```

## `check.py`: the checks

It checks prose only. It skips front matter, code blocks, inline code, links and images.

| Rule | Level | Example |
|---|---|---|
| `quotes` | ERROR | `"текст"` → `«текст»` |
| `double-hyphen` | ERROR | `--` |
| `calque` | ERROR or WARN | `имеет смысл`, `человек в цикле`, `лишние расходы`, `является` |
| `glossary` | ERROR | a spelling from the `Не писать` column of the book glossary, with its inflected forms |
| `dash-before-eto` | WARN | `Партиция это часть` → `Партиция — это часть` |
| `term-drift` | WARN | the page has `потребителей` (3) and `consumer` (32) |
| `choppy` | WARN | 4 or more sentences of 6 words or less in a row, in one paragraph |
| `same-opener` | WARN | three sentences in a row start with the same word |
| `long-sentence` | WARN | more than 30 words |
| `decimal-point` | WARN | `0.85` in prose → `0,85`. Versions and chapter numbers are skipped |
| `yo` | WARN | `еще`, `объем` → `ещё`, `объём` |
| `doubled-word` | WARN | `что что` |
| `range-hyphen` | WARN | `00-99` → `00–99`. `2025-05` is a date, it is skipped |
| `hyphen-as-dash` | WARN | ` - ` between words |
| `arrow` | WARN | `→` in prose |

- Exit code is 1 if there is an ERROR. Use `--strict` to fail on WARN too.
- `--summary` prints counts per rule. `--only rule1,rule2` shows only some rules.
- A WARN is a question, not an order. `dash-before-eto` and `term-drift` can be wrong.
- Silence a false positive:
  - one line: put `<!-- ru-proofread:ignore-line -->` on the line before;
  - a block: `<!-- ru-proofread:ignore-start -->` … `<!-- ru-proofread:ignore-end -->`.

## `check.py --stats`: rhythm

Prints three numbers per page and says `ok` or `LOW`.

| Number | Target | Dry page |
|---|---|---|
| Median words per sentence | 8 or more | 5–6 |
| Sentences of 5 words or less | 30% or less | 40–57% |
| Link words per 100 sentences | 10 or more | 3–5 |

The targets come from our best-reading summary (Data Warehouse Toolkit). They are constants at the top of `check.py`. They are a guide, not a goal. A page with many steps and definitions can stay below them.

## `check.py --before OLD NEW`: guard

Run it after every agent pass. It fails if proofreading changed something it must not change.

| Rule | Level |
|---|---|
| `code-changed`, `inline-code-changed` | ERROR |
| `link-changed` (links and image paths) | ERROR |
| `number-changed` (digits in prose) | ERROR |
| `heading-changed`, `front-matter-changed` | ERROR |
| `line-count` (needed for `compare.py`) | WARN |
| `length` (default limit 5%, `--max-change 10` after the flow pass) | WARN |

## `check.py --fix`: safe fixes

It rewrites the file. It changes only two things:

- `"текст"` → `«текст»`;
- `00-99` → `00–99`.

It skips headings (a changed heading changes its anchor), code, links, JSON-like text and lines with nested quotes. After the change it runs the guard on the file and does not write it if the guard fails. On a copy of the whole site it fixed 122 of 145 quote errors and 125 of 131 ranges. The rest need a human.

## The two agent passes

**Correctness review** (`review-prompt.md`). Typical catches:

| Before | After | Problem |
|---|---|---|
| `запускает на обновление` | `запускает при каждом обновлении` | wrong preposition |
| `Книга проверяет, есть ли…` | `В примере книги задача проверяет…` | the book does a human action |
| `Consumer пишет шаблон и падает` | `В consumer написан шаблон, и он падает` | wrong subject |
| `Автор советует настоящий URI` | `Автор советует использовать настоящий URI` | missing verb |
| `потребитель` next to `consumer` | `consumer` everywhere | term drift |

**Flow pass** (`flow-prompt.md`). It links sentences, joins halves of one thought, unfolds fragments. It must not add facts or a cause the text does not state. «Поэтому» and «потому что» are claims.

Both agents write a change log `Line | Было | Стало | Тип | Почему` and a list of **meaning risks**. Meaning risks go to the owner in the final report. Not on the page.

## Grow the rules

Each time you find a silly mistake, add it. Use real examples.

| You found | Add it to |
|---|---|
| A phrase that repeats | one line in `calques.tsv` (regex, better wording, `error` or `warn`, why) |
| A pattern with a rule | one row in `.claude/skills/ru-proofread/references/rules.md` |
| A wrong term | the `Не писать` column of the book glossary |
| Two forms of one term | one line in `term-pairs.tsv` |
| Any change in `check.py` | one case in `test_check.py`, then `python3 -I scripts/ru-proofread/test_check.py` |

## Results so far

| Chapter | Script on the original | Correctness review | Flow pass |
|---|---|---|---|
| DDIA ch 6 (Partitioning) | 10 findings, all real | 28–31 changes (two runs, about 20 in common) | not run |
| Airflow ch 4 (Asset-aware scheduling) | 5 errors, 8 warnings | 33 changes, 2 meaning risks, length +1.3% | 23 lines changed, length +3.3%. Median 7 → 8 words, short sentences 34% → 24%, link words 10 → 22 per 100. 6 link words listed as meaning risks. Guard passed |

## Limits

- The agents are the same model family as the author. There is no human ground truth. Spot-check the change logs.
- Meaning risks need the book. The agent often does not have it.
- The script knows Russian only by regex. It has no morphology. `dash-before-eto` misses some definitions.
- The rhythm numbers are a proxy for "pleasant to read". The owner decides if a page reads well.
- One review costs about 80–125k tokens per chapter. One reviewer misses about a third of what two find.
- Existing pages have problems the script will report (straight quotes, missing dashes, dry paragraphs). They are fixed chapter by chapter.
