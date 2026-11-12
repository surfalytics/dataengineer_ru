# Airflow book examples check

Checks every `python` block in `src/content/docs/book-summaries/engineering/data-pipelines-with-apache-airflow/` on a real Airflow 3.

```bash
scripts/airflow-book-check/check.sh          # from repo root, needs uv
AIRFLOW_VERSION=3.4.0 scripts/airflow-book-check/check.sh
```

What it does:

1. Imports every block. DAG files go through `DagBag`. Fails on import errors and deprecation warnings.
2. Runs `airflow dags test` for the DAGs that need no external systems (list `LOCAL` in `check.sh`).
3. Runs `test_snippets.py` (hooks, operators, triggers, helpers with mock) and the two tests from chapter 10.

Blocks for Docker, Kubernetes, Kafka, S3 and HTTP are only imported. They need real services to run.

The venv and Airflow home live in `$TMPDIR/airflow-book-check` (set `WORK` to change it).
When you add or change a block, update `LOCAL` or `test_snippets.py` if needed, and run the script before commit.
