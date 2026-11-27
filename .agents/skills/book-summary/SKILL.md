---
name: book-summary
description: Turn a prepared PDF or EPUB book plan into Russian chapter summaries for dataengineer.ru, with diagrams, proofreading, and an EPUB. Use to draft, resume, or review a book summary.
---

# Summarize a book

Work from the dataengineer.ru repository root. Start from the confirmed `book-plan.json` produced by [book-prep](../book-prep/SKILL.md). If given only a PDF or EPUB, prepare the plan first. Read the [project book guide](../../../.claude/skills/book-summary/SKILL.md) for editorial, code and diagram conventions. Follow the stages below for orchestration.

Use one chapter at a time and keep the extracted source, proofreading snapshots and stage markers in the plan's scratch directory. Selected chapters (such as `only: [1]`), `skipBook`, and review of existing pages (`reviewOnly`) skip whole-book assembly. In review mode skip drafting, resizing and rendering.

## Per chapter

1. **Resume.** Run `python3 -I scripts/book-tools/pipeline_state.py "<scratch>" "<n>|<src>|<repo-relative page>"`. Skip stages with valid markers and artifacts from the same source and run settings. If a source, diagram spec or draft changes, invalidate the affected markers and redo their downstream checks for that chapter. Explicit `redo` reruns the applicable stages for the selected chapters.
2. **Write and size.** Read the chapter and glossary. Use `python3 -I scripts/book-tools/words.py --sections "<src>"` to budget the draft. Retell the main ideas, evidence and caveats in Russian in source order, aiming for 30% of the source prose and checking the initial 20–40% range with `words.py --source "<src>" "<page>"`. Place the chapter in `src/content/docs/book-summaries/<group>/<slug>/<file>`. Use the plan titles and links, preserve editorial additions and existing URLs when revising, and mark original explanations as the project guide specifies. Write diagram specs and any runnable code in the repo's established layout. Run `check.py --glossary "<glossary>" "<page>"` and fix errors before recording `write`.
3. **Render.** For flow and architecture diagrams, use the [Excalidraw adapter setup](../../../scripts/book-tools/README.md#excalidraw-for-codex). Run the chapter's diagram script from the repo root and inspect its PNGs or a contact sheet. Check labels, bounds, arrows and the page's image paths. Record `diagrams` after the rendered assets pass, or when the chapter requires zero diagrams. Use the project [diagram guide](../../../.claude/skills/diagrams/SKILL.md) for ER diagrams and image conventions.
4. **Review.** Save a pre-review copy as `<scratch>/before/chNN.md` and reuse it when resuming the same draft. Use the project's [review prompt](../../../.claude/skills/ru-proofread/references/review-prompt.md) as the correctness checklist and verify meaning against the source. Run the glossary check and `check.py --before "<before>" "<page>"`. If `check.py --stats` reports `LOW` or the style check flags `choppy`, apply the [flow pass](../../../.claude/skills/ru-proofread/references/flow-prompt.md) and guard with `--max-change 10`. Apply the [clarity pass](../../../.claude/skills/ru-proofread/references/clarity-prompt.md), recheck with `--max-change 20` and the glossary, and measure again. When clarity requires additions, the final text can reach 50%. Record `review`, `flow` (when run) and `clarity` only after each pass succeeds.
5. **Check runnable examples.** For books with code examples, choose a pinned local environment before the first chapter. When `checkCode` is requested, run `python3 -I scripts/book-tools/check_code.py "<page>" --code-dir "scripts/<scriptsPrefix>-code" --runner "<codeRunner>" --json` (`python3` is the default runner). Fix flagged examples using real output. Mark examples that need an unavailable environment with `# не запускается: <причина>`. Record `code` after resolving the findings and report skipped examples.

Record successful stages as empty files `<scratch>/state/chNN.<stage>.done`. Run Python tools with their repository-relative paths under `scripts/book-tools/` or `scripts/ru-proofread/`. If a stage fails, leave its marker absent and report the specific failure.

## Finish the book

Once every planned chapter passes its required stages, merge chapter registers with `python3 -I scripts/book-tools/merge_registers.py "<scriptsPrefix>"`. Follow the [lead guide](../../../.claude/skills/book-summary/references/lead.md) for the overview, nav, summary index, optional library link and cover. Check chapter titles and previous/next links across the book.

Follow the [EPUB guide](../../../.claude/skills/book-epub/SKILL.md) to assemble and validate the download. Run `npm run build` and check the book cover in the built carousel. After a full or partial run, record the current state with `python3 -I scripts/book-tools/status.py "<slug>" --group "<group>" --title "<title>" --scratch "<scratch>" --chapters "<comma-separated planned chapter numbers>"`. Report completed chapters, final sizes, build checks when run, and open issues.
