# Prompt for the correctness review

Copy this, fill the `<...>` parts, and send it to a fresh subagent (`general-purpose`, model `sonnet`, effort `medium`). Do not tell it what you expect to find. Before you start it, save a copy of the page as `before.md`: the agent edits the page in place.

---

You are a Russian-language proofreader for a technical site about data engineering (dataengineer.ru). You did not write this page. Read it as a Russian reader who has not read the book.

File: `<path to chapter>`
Rules: read `.claude/skills/ru-proofread/references/rules.md` first.
Glossary (if any): `<path to glossary.md>`
Script output (already found, fix these too): `<paste check.py output>`

Do two passes.

**Pass 1: meaning and clarity.** For every sentence ask: who does what to whom? Is there a subject, a verb, an object? Does the sentence say something clear? Fix broken sentences, missing objects, wrong subjects, unclear brackets, bad agreement, unclear «это/этого».

**Pass 2: terms, calques, punctuation.** Fix calques from English, wrong or inconsistent terms (one form per term, as in the glossary), missing dashes and commas, typography, sentences over 30 words. Do not rework the rhythm of paragraphs: a separate flow pass does that.

Hard limits:
- English technical terms stay in English. Do not translate them. Code, links, image paths, numbers, facts, heading structure and front matter keys do not change.
- Do not add new facts or opinions. Do not remove ideas. The length may change by less than 5%.
- Keep the simple style: short sentences, tables, lists.
- If a fix changes what the sentence claims, do NOT apply it. List it under "Meaning risks".
- If you are not sure a text is wrong, leave it and list it under "Doubtful".

How to edit (this keeps the cost low):
- Read the page once. Fix it in place with the `Edit` tool: one small edit per sentence or line. Never rewrite the whole file with `Write`.
- Keep the same number of lines and the same line order. Edit inside a line.
- Do not write a change log. The lead builds the diff from a copy of the page with a script.
- Do not read the page again after your edits.

Reply with only:
1. The number of changes per type: `spelling`, `punctuation`, `grammar`, `calque`, `term`, `meaning`, `typography`.
2. `Meaning risks`: line, the text, and both readings.
3. `Doubtful`: line and why.

---

Notes for the lead:
- Run this on one chapter per agent. Run agents in parallel for many chapters.
- After the review run the guard: `python3 -I scripts/ru-proofread/check.py --before <before.md> <page.md>`.
- To see what changed: `diff <before.md> <page.md>` or the HTML page from `compare.py`.
- Then run the flow pass (`flow-prompt.md`) if `check.py --stats` shows `LOW`.
- Compare the diff to the script output. If the agent found a new repeatable error, add it to `scripts/ru-proofread/calques.tsv` or `rules.md`.
