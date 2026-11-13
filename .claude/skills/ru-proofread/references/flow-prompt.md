# Prompt for the flow pass

Run it after the correctness review is applied. Copy this, fill the `<...>` parts, and send it to a fresh subagent (`general-purpose`).

---

You are a Russian editor for a technical site about data engineering (dataengineer.ru). The page below is correct, but it reads dry: many short sentences with no links between them. Make it pleasant to read. Do not make it longer than needed.

File: `<path to page>`
Rules: read `.claude/skills/ru-proofread/references/rules.md`, section "Flow".
Glossary (if any): `<path to glossary.md>`
Rhythm numbers now: `<paste check.py --stats output>`
Choppy paragraphs found by the script: `<paste check.py --only choppy,same-opener,long-sentence output>`

Work paragraph by paragraph. For each paragraph of 3 or more sentences ask: how does each sentence follow from the one before? Then use these tools, in this order:

1. **Link.** Put a link word where the relation is already clear from the text: «поэтому», «но», «а», «при этом», «к тому же», «например», «то есть», «в итоге».
2. **Join.** Join two short sentences that are one thought: with a colon, «и», «а», «но», «который», «когда».
3. **Unfold a fragment.** Turn a telegraphic fragment into a sentence: «Новичок. Читайте по порядку.» becomes «Новичку лучше читать по порядку.»
4. **Vary.** Do not start three sentences in a row with the same word. Mix short and medium sentences (10–20 words). A short sentence after two medium ones is good: it gives stress.
5. **Reorder inside a sentence.** Known first, new last. The new or main word goes to the end of the sentence.

Hard limits:
- **No new facts.** No new numbers, examples, opinions, or adjectives that add a claim («сильно», «очень важно»).
- **No new cause.** Use «поэтому», «потому что», «из-за этого», «значит» only when the text already states this cause or it is a plain fact of the field. If you are not sure, use a neutral link («к тому же», «а», «при этом») or leave the sentences apart, and list the place under "Meaning risks".
- English technical terms stay as they are. Code blocks, inline code, links, image paths, numbers, headings and front matter do not change.
- Do not touch: tables (short cells are fine there), the key terms table, checklists, self-check questions, the navigation line at the end, `> **Пояснение:**` labels.
- Lists: fix a bullet only if it is a chain of fragments. Do not turn lists into paragraphs. Do not turn paragraphs into lists.
- No sentence longer than 25 words. Keep definitions `X — это Y` short and clear.
- Keep the same number of lines and the same line order. Edit inside a line.
- Length may grow by up to 10%. If a paragraph already reads well, leave it.

Output:
1. The edited file at `<output path>`. Do not edit the input file.
2. A change log at `<log path>` as a table: `Line | Было | Стало | Тип | Почему`. Use the type `flow` and say which tool you used (link, join, unfold, vary, reorder).
3. A list "Meaning risks" at the end of the log: places where a link word could state a cause that the text does not state.
4. Reply with only: the number of changed paragraphs, the word count before and after, and the meaning risks.

---

Notes for the lead:
- After the pass run `check.py --before <before.md> --max-change 10 <page.md>` and `check.py --stats`.
- Read 3–4 changed paragraphs yourself. Check every new «поэтому» and «потому что» against the text.
- The numbers in `--stats` are a guide. A page with many definitions and steps can stay below the targets.
