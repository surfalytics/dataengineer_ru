#!/usr/bin/env python3
"""Run all ```sql blocks of a chapter (in order, one in-memory DuckDB session).
Usage: check_sql.py <chapter.md> [...]   Exit code 1 on any SQL error."""
import re, subprocess, sys

fence = re.compile(r"```sql\n(.*?)```", re.S)
bad = 0
for path in sys.argv[1:]:
    text = open(path, encoding="utf-8").read()
    blocks = fence.findall(text)
    if not blocks:
        print(f"WARN {path}: no sql blocks"); bad += 1; continue
    script = "\n".join(blocks)
    r = subprocess.run(["duckdb", "-bail", ":memory:"], input=script, text=True, capture_output=True)
    if r.returncode != 0:
        print(f"FAIL {path}\n{r.stderr.strip()[:1500]}"); bad += 1
    else:
        print(f"OK   {path} ({len(blocks)} blocks)")
sys.exit(1 if bad else 0)
