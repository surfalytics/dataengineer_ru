# Book summaries: status

One row per book. Update it after every run or PR. `python3 -I scripts/book-tools/status.py --help` changes a row. The `book-summary` workflow runs it at the end of each run.

| Status | Meaning |
|---|---|
| `done` | Every chapter went through write, review, flow (if needed) and clarity. Overview, nav, cover and EPUB are in place. |
| `needs review` | Written before the review and clarity steps existed (before #101). Run `book-prep`, then `book-summary` with `reviewOnly: true` (add `checkCode: true` for technical books). |
| `in progress` | Some chapters are not done. "What is left" lists them. |

| Book | Folder | Chapters | Status | Last revision | PR | What is left |
|---|---|---|---|---|---|---|
| Fundamentals of Data Engineering | `engineering/fundamentals-of-data-engineering` | 11 | done | 2026-11-16 | #108 | — |
| The Data Warehouse Toolkit | `engineering/data-warehouse-toolkit` | 21 | done | 2026-11-15 | #105 | — |
| Designing Data-Intensive Applications, 2nd ed. | `engineering/designing-data-intensive-applications` | 14 | done | 2026-11-15 | #106 | — |
| DuckDB: Up and Running | `engineering/duckdb-up-and-running` | 9 | done | 2026-11-16 | #108 | — |
| Data Pipelines with Apache Airflow | `engineering/data-pipelines-with-apache-airflow` | 17 | done | 2026-11-15 | #105 | — |
| Data Engineering Design Patterns | `engineering/data-engineering-design-patterns` | 10 | done | 2026-11-16 | #108 | — |
| Data Quality Fundamentals | `engineering/data-quality-fundamentals` | 10 | done | 2026-11-15 | #103 | — |
| Analytics Engineering with SQL and dbt | `engineering/analytics-engineering-with-sql-and-dbt` | 6 | done | 2026-11-15 | #105 | — |
| Redefining Data Engineering with AI | `engineering/redefining-data-engineering-with-ai` | 2 | done | 2026-11-15 | #103 | Early Release: add chapters when they come out |
| AI Engineering | `ai/ai-engineering` | 10 | done | 2026-11-16 | #108 | reviewed against the German edition (only copy); recheck with the English original if available |
| Machines that Think: What it really means for AI to think (MEAP v3) | `ai/machines-that-think` | 8 | done | 2026-11-16 | #108 | MEAP v3: chapters 9-12 not out yet |
| Claude Code: Up and Running | `ai/claude-code-up-and-running` | 4 | done | 2026-11-15 | #103 | Early Release: add chapters when they come out |
| Claude AI Bible | `ai/claude-ai-bible` | 22 | done | 2026-11-15 | #101 | — |
| The Startup Owner's Manual | `entrepreneurship/startup-owners-manual` | 16 | done | 2026-11-16 | #108 | — |
| The Mom Test | `entrepreneurship/mom-test` | 9 | done | 2026-11-16 | #108 | — |
| The Diary of a CEO | `entrepreneurship/diary-of-a-ceo` | 33 | done | 2026-11-16 | #108 | — |
| Lean Analytics | `business/lean-analytics` | 31 | done | 2026-11-15 | #104 | — |
| Escaping the Build Trap | `business/escaping-the-build-trap` | 26 | done | 2026-11-15 | #104 | — (checked 2026-11-16: all chapters 31-51%; pages are short because the book chapters are short) |
| The Staff Engineer's Path | `business/staff-engineers-path` | 10 | done | 2026-11-16 | #107 | — |
| Staff Engineer: Leadership beyond the management track | `business/staff-engineer` | 8 | done | 2026-11-16 | #107 | — |
| The Manager's Path | `business/managers-path` | 10 | done | 2026-11-16 | #107 | — |
| Engineering Leadership: The Hard Parts | `business/engineering-leadership-hard-parts` | 11 | done | 2026-11-16 | #110 | — |
| Crafting Engineering Strategy | `business/crafting-engineering-strategy` | 24 | done | 2026-11-16 | #110 | — |
| The Engineering Executive's Primer | `business/engineering-executives-primer` | 24 | done | 2026-11-16 | #110 | — |
| Learning Spark, 2nd Edition | `engineering/learning-spark` | 12 | done | 2026-11-24 | #113 | — |
| Practical Lakehouse Architecture | `engineering/practical-lakehouse-architecture` | 8 | done | 2026-11-27 | #117 | — |
| Apache Iceberg: The Definitive Guide | `engineering/apache-iceberg-the-definitive-guide` | 14 | done | 2026-11-27 | #116 | — |
