# ru-proofread: how it works

Tools and rules to make our Russian text read like Russian, not like a translation.

- Technical terms stay in English (`hot spot`, `grain`, `scatter/gather`). We do not translate them.
- We fix the Russian around them: calques, missing dashes, broken sentences, flow.
- The skill is in `.claude/skills/ru-proofread/`. This folder has the scripts and data.

## Why three steps

One tool is not enough. We tested on two chapters (DDIA ch 6, Airflow ch 4).

| Tool | What it found | Verdict |
|---|---|---|
| LanguageTool (local) | Almost nothing real. Flags `партиционирование` as a typo | Not used |
| `typograf` | Breaks Markdown (`- ` bullets, `**bold:**`) | Not used |
| `check.py` (this folder) | Fixed patterns. Every finding was real | Step 1 |
| Fresh review agent | Broken sentences, wrong subjects, wrong terms. About 2/3 of all fixes | Step 2 |

## Folder

| File | What it does |
|---|---|
| `check.py` | Deterministic checks on Markdown prose. Standard library only |
| `calques.tsv` | Calques and stop words. One line per rule. Grows over time |
| `compare.py` | Builds a before/after HTML page to review the changes |

Rules and the review prompt: `.claude/skills/ru-proofread/references/`.

## Quick start

```bash
# Step 1: script
python3 -I scripts/ru-proofread/check.py src/content/docs/book-summaries/<group>/<book>/<chapter>.md
python3 -I scripts/ru-proofread/check.py --glossary scripts/<book>-diagrams/glossary.md <chapter>.md

# Step 2: ask Claude
#   "Use ru-proofread on <chapter>"   (it starts a fresh review agent)

# Step 3: re-run step 1 until no ERROR is left, then compare
python3 -I scripts/ru-proofread/compare.py before.md after.md changes.md /tmp/compare.html "Title"
open /tmp/compare.html
```

## Step 1: the script

It checks prose only. It skips front matter, code blocks, inline code, links and images.

| Rule | Level | Example |
|---|---|---|
| `quotes` | ERROR | `"текст"` → `«текст»` |
| `double-hyphen` | ERROR | `--` |
| `calque` | ERROR or WARN | `имеет смысл`, `человек в цикле`, `лишние расходы`, `является` |
| `glossary` | ERROR | a spelling from the `Не писать` column of the book glossary |
| `dash-before-eto` | WARN | `Партиция это часть` → `Партиция — это часть` |
| `range-hyphen` | WARN | `00-99` → `00–99` |
| `hyphen-as-dash` | WARN | ` - ` between words |
| `arrow` | WARN | `→` in prose |
| `long-sentence` | WARN | more than 30 words |
| `same-opener` | WARN | three sentences in a row start with the same word |

- Exit code is 1 if there is an ERROR. Use `--strict` to fail on WARN too.
- `--summary` prints counts per rule. `--only rule1,rule2` shows only some rules.
- `dash-before-eto` looks only at the first 6 words of a sentence. It can still miss cases or flag a few good ones. A WARN is a question, not an order.
- Silence a false positive:
  - one line: put `<!-- ru-proofread:ignore-line -->` on the line before;
  - a block: `<!-- ru-proofread:ignore-start -->` … `<!-- ru-proofread:ignore-end -->`.

## Step 2: the fresh review agent

The script cannot read meaning. A fresh agent can. It did not write the text, so it is more critical.

- The prompt is in `.claude/skills/ru-proofread/references/review-prompt.md`.
- Pass 1 is meaning: who does what to whom? Subject, verb, object?
- Pass 2 is terms, calques, punctuation and flow.
- It writes a corrected file and a change log `Line | Было | Стало | Тип | Почему`.
- It does **not** apply a fix that changes what a sentence claims. It lists it under `Meaning risks`.
- Meaning risks go to the owner in the final report. Not on the page.

Typical catches:

| Before | After | Problem |
|---|---|---|
| `запускает на обновление` | `запускает при каждом обновлении` | wrong preposition |
| `Книга проверяет, есть ли…` | `В примере книги задача проверяет…` | the book does a human action |
| `Consumer пишет шаблон и падает` | `В consumer написан шаблон, и он падает` | wrong subject |
| `Автор советует настоящий URI` | `Автор советует использовать настоящий URI` | missing verb |
| `потребитель` next to `consumer` | `consumer` everywhere | term drift |

## Step 3: apply, re-run, compare

1. Apply the changes you agree with. Facts, numbers, code, links and front matter do not change.
2. Run step 1 again. No ERROR is left.
3. Length changes by less than 5%.
4. Open the compare page. Red is removed text. Green is new text. Each changed line has its type and reason.

## Grow the rules

Each time you find a silly mistake, add it. Use real examples.

| You found | Add it to |
|---|---|
| A phrase that repeats | one line in `calques.tsv` (regex, better wording, `error` or `warn`, why) |
| A pattern with a rule | one row in `.claude/skills/ru-proofread/references/rules.md` |
| A wrong term | the `Не писать` column of the book glossary |

## Results so far

| Chapter | Script on the original | Review agent | After |
|---|---|---|---|
| DDIA ch 6 (Partitioning) | 10 findings, all real | 28–31 changes (two runs, about 20 in common) | script: 0 |
| Airflow ch 4 (Asset-aware scheduling) | 5 errors, 6 warnings | 33 changes, 2 meaning risks | script: 0, code blocks identical, length +1.9% |

## Limits

- The review agent is the same model family as the author. There is no human ground truth. Spot-check the change log.
- Meaning risks need the book. The agent often does not have it.
- The script knows Russian patterns only by regex. It has no morphology.
- Existing pages have problems the script will report (straight quotes, missing dashes). They are fixed chapter by chapter, not in this change.
