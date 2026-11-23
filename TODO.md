# TODO

What to do next. Update this file when you finish a step or plan a new one.

## Lecture summaries («Конспекты лекций»)

How to work: the `lecture-summary` skill. Courses that are started: `scripts/lecture-tools/status.md`.

Each planned course already has a page «О курсе» on the site (summary, lecture list, links) and the badge «скоро» in `src/nav.mjs`.

### Next steps

- [x] PR #112: the lecture pipeline, the «Конспекты лекций» tab, CME295 lecture 1, the «О курсе» pages.
- [ ] CME295 lectures 2-7, in one run. Run `lecture-prep` again (the transcripts were in a temporary folder), then `lecture-summary` with `"only": [2, 3, 4, 5, 6, 7]` and `"publish": true`. About $16.
- [ ] CS336. Start its glossary from `scripts/cme295-diagrams/glossary.md`. About $44.
- [ ] CS329Z, when its 2 private videos are public. About $25.
- [ ] CS193T. About $16.
- [ ] CS50x. First add C to "Code and practice" in the skill: compile with `clang`, show the real output. About $38.

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
