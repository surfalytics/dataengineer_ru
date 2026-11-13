#!/usr/bin/env python3
"""Собирает страницу главы 4 из шаблона templates/ch04.tpl.md.
1) Запускает все ```sql блоки шаблона по порядку в одной базе DuckDB (файл во временной папке) и подставляет
   настоящий вывод вместо маркеров {{sqlout: N}} (N = номер sql-блока, с 1).
2) Сохраняет весь SQL страницы в ch04_practice.sql.
3) Вызывает embed.py: вставляет вывод Python-скриптов вместо {{out: file.py}}.
Запуск: python3 scripts/data-quality-fundamentals-code/ch04_build_page.py"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TPL = HERE / "templates" / "ch04.tpl.md"
PAGE = ROOT / "src/content/docs/book-summaries/engineering/data-quality-fundamentals/04-monitoring-anomaly-detection.md"

text = TPL.read_text(encoding="utf-8")
blocks = re.findall(r"```sql\n(.*?)```", text, flags=re.S)
outputs = {}
with tempfile.TemporaryDirectory() as tmp:
    db = str(Path(tmp) / "ch04.duckdb")
    for i, sql in enumerate(blocks, 1):
        r = subprocess.run(["duckdb", "-bail", db], input=sql, text=True, capture_output=True)
        if r.returncode != 0:
            raise SystemExit(f"sql block {i} failed:\n{r.stderr}")
        outputs[i] = r.stdout.rstrip("\n")

(HERE / "ch04_practice.sql").write_text("\n".join(blocks), encoding="utf-8")


def sub(m):
    n = int(m.group(1))
    if not outputs.get(n):
        raise SystemExit(f"sql block {n} has no output")
    return f"```text\n{outputs[n]}\n```"


with tempfile.TemporaryDirectory() as tmp:
    mid = Path(tmp) / "ch04.mid.md"
    mid.write_text(re.sub(r"^\{\{sqlout:\s*(\d+)\}\}$", sub, text, flags=re.M), encoding="utf-8")
    subprocess.run([sys.executable, str(HERE / "embed.py"), str(mid), str(PAGE)], check=True, cwd=ROOT)
