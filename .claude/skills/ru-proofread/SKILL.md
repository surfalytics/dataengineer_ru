---
name: ru-proofread
description: Proofread Russian text on dataengineer.ru so it reads clearly and pleasantly - fixes calques from English, missing dashes, wrong or missing objects, awkward flow and typography, and keeps technical terms in English. Use after writing or editing any Russian page (book summary, practice lesson, article), when the user asks to вычитать, проверить русский, улучшить текст, fix calques, or when Russian text sounds like a translation.
---

# Russian proofreading (вычитка)

Goal: the page reads like it was written in Russian, not translated. The reader should feel no friction.

Technical terms stay in English (`grain`, `hot spot`, `scatter/gather`). We do not translate them. We only make the Russian around them correct and smooth.

Guide for humans, with test results: `scripts/ru-proofread/README.md`.

## When to run

- After you finish a chapter or page, before `npm run build` and before commit.
- On any page the user calls "rough", "like a translation", or "silly mistakes".
- Workers that write chapters in parallel run it on their own chapter. The lead runs it once more on shared pages (`index.md`).

## The pipeline (3 steps, in this order)

### Step 1. Run the script

```bash
python3 -I scripts/ru-proofread/check.py <file-or-folder>
python3 -I scripts/ru-proofread/check.py --glossary scripts/<book>-diagrams/glossary.md <chapter.md>
```

- It checks prose only. It skips front matter, code, inline code, links.
- `ERROR` must be fixed. `WARN` is a question: fix it or decide it is fine.
- It finds: straight quotes, `--`, calques and stop words (`scripts/ru-proofread/calques.tsv`), missing dash before `это`, hyphen in ranges (`00-99`), long sentences, three sentences with the same first word, wrong term spelling (glossary column `Не писать`).
- Silence a false positive: put `<!-- ru-proofread:ignore-line -->` on the line before it.
- The script cannot judge meaning. That is step 2.

### Step 2. Review with a fresh agent

Use a **fresh subagent** that did not write the text. It has no memory of the draft, so it is more critical. Give it:

- the chapter path;
- `references/rules.md` (error classes and flow rules);
- the glossary of the book, if it exists;
- the output of step 1.

Use the prompt in `references/review-prompt.md`. The agent returns a table `Line | Было | Стало | Тип | Почему` and a list of **meaning risks**. It also writes the corrected file, but you apply only the changes you agree with.

Why a fresh agent and two passes: in our test on DDIA chapter 6, two independent reviews found about 20 of the same errors and a few different ones. The review without rules was better at broken sentences. The review with term and calque rules was better at wrong terms. The script found only fixed patterns, but all of its findings were real.

### Step 3. Apply and re-run

1. Apply the changes. Keep the facts, numbers, code, links, image paths and front matter keys unchanged.
2. Run step 1 again. No `ERROR` is left.
3. Check the length: the page must stay within the size target of the `book-summary` skill. Proofreading should change length by less than 5%.
4. Put **meaning risks** in your final report, not on the page. The owner does not want translation notes on pages.

## What counts as a meaning risk

Report these to the lead, do not decide alone:

- the fix changes what a sentence claims (for example `общая задача` → `частный случай задачи`);
- an unclear passage where you cannot tell what the book says;
- a number, name, or term that looks wrong.

If the original book is not in front of you, say so.

## Rules in short (full list in `references/rules.md`)

1. Definition `X — это Y` needs a dash. Not `X это Y`.
2. Every verb has its object and the right subject. Not "он путает", not "чтение должно читать".
3. No calques. Not "имеет смысл", "человек в цикле", "справедливо распределена", "лечат проблему".
4. Do not translate technical terms. Do translate the words around them.
5. One idea per sentence, but vary the rhythm. Link sentences with "поэтому", "но", "то есть".
6. Typography: «ёлочки», `—` as dash, `–` in ranges, `0,85` in text.

## Grow the rules

Each time you find a silly mistake, add it:

- a repeatable phrase → one line in `scripts/ru-proofread/calques.tsv`;
- a repeatable pattern → one example in `references/rules.md`;
- a wrong term → `Не писать` column in the book glossary.

Do not add vague rules. Add examples from real pages.
