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

Third run: "Claude AI Bible" (22 chapters, 94,000 source words), 2026-11-14. First full-size book.

| Step | Model | Agents | Est. $ | Note |
|---|---|---|---|---|
| Split + glossary (66 terms) | sonnet | 2 | 0.49 | |
| Status | haiku | 1 | 0.01 | |
| Write 22 chapters | opus/high | 22 | 34.63 | $0.37 per 1,000 source words |
| Review | sonnet/medium | 22 | 2.95 | 0-7 changes per chapter |
| Flow | opus/medium | 2 | 0.68 | Only ch4 and ch6 were LOW |
| Book + build | opus + sonnet | 2 | 2.85 | Aligned 14 chapter titles, removed 1 duplicate diagram, settled glossary clashes |
| **Total** | | **51** | **41.61** | 19 minutes for Part 2 |

Section budgets did not stop long drafts: 6 writers report first drafts of 53-74%. All final pages are 36-40%.

Clarity pass added later (from #103), run on the finished 22 chapters, 2026-11-15:

| Step | Model | Agents | Est. $ | Note |
|---|---|---|---|---|
| Clarity | opus/high | 22 | 10.93 | $0.50 per chapter. 319 changes (8-23 per chapter), 0 deletions. Pages grew 2-8% |
| Status | haiku | 1 | 0.01 | |

The review had made 0-7 changes per chapter. The clarity pass found 8-23 more: vague sentences, unclear «это», slang and calques the script did not know. 12 repeatable ones went to `calques.tsv`.

What we learned:

- Writers are 64% of the cost. In a writer, output is about 43% of the cost, cache writes 29%, cache reads 28%.
- Cost grows with turns: every turn re-reads the whole context. Ch2 had 45 turns and 6M cache-read tokens.
- Every agent starts with about 45K tokens of base context (system prompt, tools, CLAUDE.md). That alone is $0.01 on haiku, $0.12 on sonnet.
- Rough estimate: about $0.35 per 1,000 source words for chapters, plus $2-3 per book for prep and book steps.

How to measure a run:

```bash
python3 -I scripts/book-tools/token_usage.py ~/.claude/projects/<project>/<session>/subagents/workflows/wf_<id>
```

Fourth run: "Designing Data-Intensive Applications, 2nd Edition" (14 chapters, 200,000 source words without reference lists), 2026-11-15. Full rewrite of the 1st-edition summary, old images reused. `checkCode` on.

| Step | Model | Agents | Est. $ | Note |
|---|---|---|---|---|
| Split + glossary (51 terms) | sonnet | 2 | 0.55 | Word counts included reference lists (229K). Cut them before the run |
| Write 14 chapters | opus/high | 14 | 44.98 | $0.22 per 1,000 source words. Pages 30-40% |
| Review | sonnet/medium | 14 | 2.77 | 3-7 changes per chapter |
| Clarity | opus/high | 14 | 10.89 | 12-22 changes per chapter |
| Code | sonnet/medium | 14 | 1.57 | 1 output fixed |
| Book + build | opus + sonnet | 2 | 2.98 | New book map, 2nd-edition cover, 333 glossary rows merged |
| **Total** | | **61** | **63.75** | 28 minutes for Part 2 |

Lesson: cut the reference list from each `chNN.txt` before you count words. DDIA has long reference lists, and they would raise every size target by 10-20%.
