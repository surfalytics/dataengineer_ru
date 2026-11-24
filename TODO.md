# TODO

What to do next. Update this file when you finish a step or plan a new one.

## Book workflow: test the token changes on the next book

On 2026-11-24 we changed the `book-summary` workflow to use fewer tokens. A test on one chapter did not show a saving. Test it again on the next whole book.

**How it was** (Learning Spark, 12 chapters, about 76M tokens, about $30):

- The writer drew its own diagrams. Each turn re-reads its 100-200K context, and 11-31 tool calls per writer went to diagrams.
- An LLM agent checked all the code. It missed 2 hand-written outputs in ch09.
- The Opus book step merged the registers by hand.
- The workflow returned the full report to the lead (69K characters).
- The Docker image was built after the test chapter, so ch01 ran twice.

**How it is now:**

- The writer only writes the diagram specs. A new Diagrams stage (Sonnet, small context) draws them and checks them all on one contact sheet (`contact_sheet.mjs`).
- `check_code.py` runs every python and SQL block and compares it with the page. An agent gets only the blocks it flags.
- `merge_registers.py` merges the registers.
- A short report by default. The details are in `journal.jsonl`, or use `fullReport: true`.
- The writer reads only its own inputs and applies all fixes in one turn.
- Set up the code environment (venv or Docker) before the test chapter, and pass it as `codeRunner`.

**Test on ch04 (one chapter):**

| | Old | New |
|---|---|---|
| Code check | 0.49M | 0.10M |
| Diagrams | 0.42M (inside the writer) | 0.25M |
| Writer | 2.95M | 3.91M (it read the finished pages and tool sources) |
| Total | $1.96 | $3.09 (+$0.52 flow pass, because the rhythm was LOW) |
| Blind quality score | 39.5 / 50 | 40 / 50 |

Quality did not drop. The writer limits were added after this test, so they are not tested yet.

The same changes are now in the `lecture-summary` workflow (Diagrams stage, `check_code.py`, `merge_registers.py --unit lec`, short report, writer limits). The next CME295 run (lectures 2-7) is a good first test: it is smaller than a book, and the other pages do not exist yet. Compare with lecture 1 (PR #112, old workflow).

**First real test: CME295, 7 lectures (2026-11-24).** It worked. Writers made 0 diagram runs and almost no off-task reads (14-33 turns). The code check found nothing to fix, so no fix agent ran ($0.10 per lecture). The Diagrams stage drew 28 diagrams for $1.03 and fixed 4. One lecture cost $2.50 at 35% size, against $2.30 at 22% with the old workflow. Details: "Measured cost" in `scripts/lecture-tools/README.md`.

**Next time:**

1. Run a whole new technical book with `checkCode` and `codeRunner`. Books are not tested yet in a clean run.
2. `python3 -I scripts/book-tools/token_usage.py <transcript dir>`. Compare tokens per 1,000 source words with Learning Spark (about 0.9M per 1,000 words).
3. Check the writers' turns: diagram calls should be about 0, and no reads of other pages or tool sources.
4. Read one chapter. If quality dropped, go back to the writer drawing diagrams: `git log .claude/workflows/book-summary.js`.
5. Write the result here and in "Measured cost" in `scripts/book-tools/README.md`.

## Lecture summaries («Конспекты лекций»)

How to work: the `lecture-summary` skill. Courses that are started: `scripts/lecture-tools/status.md`.

Each planned course already has a page «О курсе» on the site (summary, lecture list, links) and the badge «скоро» in `src/nav.mjs`.

### Next steps

- [x] PR #112: the lecture pipeline, the «Конспекты лекций» tab, CME295 lecture 1, the «О курсе» pages.
- [x] CME295, all 7 lectures at the new size 30-40% (lecture 1 expanded), 2026-11-24. $21 with prep.
- [ ] CS336. Start its glossary from `scripts/cme295-diagrams/glossary.md`. About $48 (18 lectures × $2.50 + $3).
- [ ] CS329Z, when its 2 private videos are public. About $33.
- [ ] CS193T. About $23.
- [ ] CS50x. First add C to "Code and practice" in the skill: compile with `clang`, show the real output. About $33-40 (long lectures).

When a course starts, its first run turns the «О курсе» page into the full overview (see `.claude/skills/lecture-summary/references/lead.md`). Then remove the «скоро» badge in `src/nav.mjs` and change «Статус» in `src/content/docs/lecture-summaries/index.md`.

### Decisions for the owner

- [ ] Which recommended courses (below) go into the plan.
- [ ] Should book summaries also show terms in two languages? Turning it on adds about 1,260 warnings to the 24 books, and their review runs would then edit many pages.

### Cost

About $2.30 per lecture of 1.5-2 hours, plus about $2.30 per run for prep and the course step (measured on CME295 lecture 1). Write many lectures in one run.

### Planned courses (chosen by the owner, 2026-11-23)

| # | Course | Playlist | Lectures | Hours | Captions | Slug, group | Practice | Est. $ | Notes |
|---|---|---|---|---|---|---|---|---|---|
| 0 | Stanford CME295 Transformers & LLMs, lectures 2-7 | `PLakGfbKCei80` | 6 left | 10.4 | manual (lecture 7: auto) | `stanford-cme295`, `ai` | python | 16 | In progress, see `status.md` |
| 1 | Stanford CS336 Language Modeling from Scratch, Spring 2026 (Percy Liang, Tatsunori Hashimoto) | `PLoROMvodv4rMqXOcazWaTUHhq-yembLCV` | 18 (17 + guest lecture) | 24.2 | manual | `stanford-cs336`, `ai` | python | 44 | Builds on CME295: start the glossary from `scripts/cme295-diagrams/glossary.md`. Code in the lectures is PyTorch on GPU: our examples stay small (numpy), GPU parts are described, not run |
| 2 | Stanford CS329Z Engineering AI Agents, Autumn 2026 | `PLPRcF5HR02_U` | 12 (2 private now) | 12.8 | manual | `stanford-cs329z`, `ai` | python | 25 | Playlist is in reverse order: prep numbers lectures by their titles. 2 videos are private (not out yet): run prep again when they are public. Has guest lectures (Terminal-Bench) |
| 3 | Stanford CS193T Thinking with AI, Autumn 2026 (Cynthia Bailey) | `PLDrJO3v_iAZY` | 7 | 7.7 | manual | `stanford-cs193t`, `ai` | none | 16 | AI literacy: how chatbots work, prompting, agents and MCP, AI risk, costs. Short and cheap. Playlist is in reverse order |
| 4 | Harvard CS50x 2025 (David J. Malan) | `PLhQjrBD2T383q7Vn8QnTsVgSvyLpsqL_R` | 13 videos (intro and lectures 0-10) | 26.4 | manual | `harvard-cs50x`, `cs` | python, duckdb | 38 | License CC BY-NC-SA 4.0: credit CS50. Lectures 1-5 teach C: before this course, add C to "Code and practice" in the skill (compile with `clang`, real output). Lectures are about 2 hours: pages will be near the 25% limit |

Playlist URL: `https://www.youtube.com/playlist?list=<ID>`.

### Recommended courses (not confirmed by the owner)

The strongest free courses on YouTube for a data engineer, from official channels only. Re-uploads by other channels are not used.

| Course | Source | Size | Why |
|---|---|---|---|
| CMU 15-445/645 Intro to Database Systems (Andy Pavlo) | CMU Database Group channel, latest fall semester ("#01 - Relational Model & Algebra (CMU Intro to Database Systems)") | about 25 lectures | How a database works inside: storage, indexes, joins, query optimizer, transactions, recovery. The best database course. Practice: duckdb |
| CMU 15-721 Advanced Database Systems, Spring 2024 (Andy Pavlo) | CMU Database Group channel ("S2024 #01 - Modern OLAP Database Systems") | about 20 lectures | How modern warehouses work: columnar storage, vectorized execution, query compilation, Snowflake, Databricks, DuckDB |
| MIT 6.824 Distributed Systems, 2020 (Robert Morris) | channel "MIT 6.824: Distributed Systems" | 20 lectures | MapReduce, Raft, replication, Spanner, consistency. A companion to our DDIA summary |
| Harvard CS50 SQL (Carter Zenke) | CS50 channel ("CS50 SQL - Lecture 0 - Querying") | 7 lectures | The friendliest SQL course. Fits our SQL practice. Practice: duckdb |
| Neural Networks: Zero to Hero (Andrej Karpathy) | `PLAqhIrjkxbuWI23v9cThsA9GvCAUhRvKZ` | 10 videos, 19.4 h | Build a neural network, a tokenizer and GPT from scratch, line by line. The best way to learn LLM basics by code. Not a university course |
| Stanford CS229 Machine Learning, Spring 2026 | `PLaqpC4kq8Gpw` | 17 videos, 20.6 h | Machine learning basics: regression, classification, neural networks, evaluation. Andrew Ng's 2018 version: `PLoROMvodv4rMiGQp3WXShtMGgzqpfVfbU` |
| Berkeley Agentic AI MOOC, Fall 2025 | `PLS01nW3RtgoqGkm4UeqNeZLccW-OGc1fJ` | 11 talks, 12.9 h | Talks by researchers and engineers who build agents. After CS329Z. Talks, not a course: each page stands alone |
| Harvard Stat 110 Probability (Joe Blitzstein) | `PLLVplP8OIVc8EktkrD3Q8td0GmId7DjW0` | 36 videos, 27.1 h | Probability, taught very clearly. Fits our statistics practice |

Checked 2026-11-23: playlists exist on official channels. Captions not yet checked for the recommended courses: `lecture-prep` reports them.
