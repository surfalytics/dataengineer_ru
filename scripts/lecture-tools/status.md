# Lecture summaries: status

One row per course. Update it after every run or PR. `python3 -I scripts/book-tools/status.py <slug> --kind lecture --help` changes a row. The `lecture-summary` workflow runs it at the end of each run.

| Status | Meaning |
|---|---|
| `done` | Every lecture went through write, review, flow (if needed) and clarity. Overview, nav and EPUB are in place. |
| `in progress` | Some lectures are not done. "What is left" lists them. |
| `planned` | Only the «О курсе» page is on the site (badge «скоро» in the menu). The plan and its order: `TODO.md`. |

| Course | Folder | Lectures | Status | Last revision | PR | What is left |
|---|---|---|---|---|---|---|
| Stanford CME295: Transformers and Large Language Models | `ai/stanford-cme295` | 7 | done | 2026-11-24 | #112 | — |
| Stanford CS336: Language Modeling from Scratch | `ai/stanford-cs336` | 0/18 | planned | 2026-11-23 | #112 | all lectures; «О курсе» page is on the site |
| Stanford CS329Z: Engineering AI Agents | `ai/stanford-cs329z` | 0/12 | planned | 2026-11-23 | #112 | all lectures; 2 videos are private now |
| Stanford CS193T: Thinking with AI | `ai/stanford-cs193t` | 0/8 | planned | 2026-11-23 | #112 | all lectures; lecture 8 is not on YouTube yet |
| Harvard CS50x: Introduction to Computer Science | `cs/harvard-cs50x` | 0/12 | planned | 2026-11-23 | #112 | all lectures; add C support to the skill first |
