# book-tools

Helpers for book summaries (`book-summary` skill) and the `book-prep` / `book-summary` workflows in `.claude/workflows/`.

| Script | What it does |
|---|---|
| `split_source.py` | PDF (by page ranges) or EPUB → `chNN.txt` text files, so agents read text, not PDF pages |
| `words.py` | Prose words of a page or source; with `--source`, page size in % (target 20-40%) |
| `same_output.py` | Runs a script 6 times, prints `same x6` or the first difference |
| `token_usage.py` | Tokens and estimated API cost per agent and phase of a workflow run |

Book text from `split_source.py` stays in the scratchpad. Never commit it.

## Measured cost

First test: "Redefining Data Engineering with AI" (Early Release, 2 chapters, 18,300 source words), 2026-11-14.
List API prices. On a subscription this shows which steps cost the most, not a bill.

| Step | Model | Agents | Est. $ | Note |
|---|---|---|---|---|
| Split | sonnet | 1 | 0.16 | |
| Glossary | opus | 1 | 1.10 | Now sonnet with 30-60 terms |
| Status | sonnet → haiku | 2 | 0.13 | Haiku run: $0.01 |
| Write ch1 (7.4K words) | opus/high | 1 | 2.19 | 23 turns |
| Write ch2 (10.9K words) | opus/high | 1 | 3.64 | 45 turns. Rebuilt the book's DuckDB RAG demo as practice (the book's repo is not public) |
| Review | sonnet/medium | 2 | 0.47 | 2 and 4 changes |
| Flow | opus/medium | 0 | 0 | Not needed: `--stats` ok |
| Book (registers, overview, nav, cover) | opus/high | 1 | 1.29 | |
| Build (EPUB, `npm run build`) | sonnet | 1 | 0.14 | |
| **Total** | | **10** | **9.12** | 29 minutes |

Second test: "Claude Code: Up and Running" (Early Release, chapters 1-4, 17,300 source words), 2026-11-14. Glossary on sonnet, status on haiku.

| Step | Model | Agents | Est. $ | Note |
|---|---|---|---|---|
| Split + glossary (39 terms) | sonnet | 2 | 0.53 | Was 1.26 with the opus glossary |
| Status | haiku | 1 | 0.01 | |
| Write ch1-ch4 | opus/high | 4 | 8.05 | 20-34 turns each. Drafts too long: ch3 was 58% before cuts |
| Review | sonnet/medium | 4 | 0.59 | 0-6 changes per chapter |
| Book + build | opus + sonnet | 2 | 1.44 | |
| **Total** | | **13** | **10.61** | 15 minutes for Part 2 (4 chapters in parallel) |

Found after the run and fixed in the workflow: a duplicate diagram in two chapters, arrow labels hiding short arrows (`excb.py` now fails on this), a draft Russian title that no step checked, first drafts far above 40% (`words.py --sections` now gives a budget per section).

What we learned:

- Writers are 64% of the cost. In a writer, output is about 43% of the cost, cache writes 29%, cache reads 28%.
- Cost grows with turns: every turn re-reads the whole context. Ch2 had 45 turns and 6M cache-read tokens.
- Every agent starts with about 45K tokens of base context (system prompt, tools, CLAUDE.md). That alone is $0.01 on haiku, $0.12 on sonnet.
- Rough estimate: about $0.35 per 1,000 source words for chapters, plus $2-3 per book for prep and book steps.

How to measure a run:

```bash
python3 -I scripts/book-tools/token_usage.py ~/.claude/projects/<project>/<session>/subagents/workflows/wf_<id>
```
