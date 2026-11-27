---
name: book-prep
description: Prepare a local PDF or EPUB for a Russian chapter-by-chapter summary on dataengineer.ru. Use to extract chapters, verify the table of contents, and hand off a book plan and glossary before writing.
---

# Prepare a book

Work from the dataengineer.ru repository root. Use a readable PDF or EPUB, a book slug in lowercase with hyphens, and one group from `engineering`, `business`, `entrepreneurship`, `ai`. Infer the slug and group when clear. Default `scriptsPrefix` to the slug. Reuse the same absolute scratch directory across runs for this source. Keep chapter text, plans and stage markers outside the Git worktree.

1. Read the table of contents and capture the title, author, publisher and year. Check `scripts/book-tools/status.md` and the book's existing summary folder for earlier work.
2. Split the source using the repo's helper:
   - **PDF:** use `pdftotext -f 1 -l 20 "<book.pdf>" -` to find the table of contents. Check the actual PDF pages against the printed chapter starts. Pass inclusive, non-overlapping PDF page ranges to `python3 -I scripts/book-tools/split_source.py "<book.pdf>" "<scratch>/src" --chapters "1:15-40,2:41-70"`. If extraction is empty or unreliable, obtain an OCR text layer and check it before splitting.
   - **EPUB:** run `python3 -I scripts/book-tools/split_source.py "<book.epub>" "<scratch>/src"`. Its `docNN.txt` files follow the spine and may cover parts of chapters. Map them to the TOC, merge or split as required, and save real chapters as `chNN.txt`. Check the EPUB XHTML directly for short chapters that the helper omitted. Keep headings and fenced code.
3. Check the beginning and end of each chapter against the TOC. Run `python3 -I scripts/book-tools/words.py "<scratch>/src"` and use counts for `chNN.txt` only. Record excluded material and its reason. A substantive preface can be chapter 0.
4. Read **Glossary first** in [the project book guide](../../../.claude/skills/book-summary/SKILL.md). Reuse relevant glossaries and `scripts/ru-proofread/calques.tsv`. Write or extend `scripts/<scriptsPrefix>-diagrams/glossary.md` with `English | Как пишем | Не писать | Пояснение`. Preserve established rows and list unresolved terms as `openQuestions`.
5. Save `<scratch>/book-plan.json` for the [book-summary skill](../book-summary/SKILL.md). Include `source` (absolute file path), `scratch`, `slug`, `group`, `scriptsPrefix`, `title`, `author`, `publisher`, `year`, `technical` (whether SQL/DuckDB practice fits), `glossary` (repo-relative path), `skipped`, `problems`, `openQuestions`, and `chapters` in book order. Each chapter has `n`, `title`, `titleRu`, `file` (`NN-<english-slug>.md`), `src` (absolute path to `chNN.txt`), `pages` (PDF range as a string, or empty for EPUB), `words`, `oldPage` (existing repo-relative page or empty) and `sql` (whether the chapter contains SQL/DuckDB examples). Retain existing chapter filenames when revising a book. Validate the JSON with `python3 -m json.tool "<scratch>/book-plan.json" >/dev/null`.

For a prep-only request, return the plan path, chapter titles, counts and ranges, skipped material and unresolved terms. For a full summary request, hand off to `book-summary` after the user has confirmed the plan or explicitly authorized proceeding with an unambiguous plan.
