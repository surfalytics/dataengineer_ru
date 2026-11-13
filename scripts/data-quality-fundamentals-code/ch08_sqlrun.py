"""Помощник для главы 8: берёт SQL-блоки из шаблона страницы, запускает их в одной сессии DuckDB
и печатает вывод блока номер BLOCK (нумерация с 1). Так вывод на странице всегда настоящий.
Запускается через ch08_out_*.py (python3 -I)."""
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
tpl = (HERE / "templates" / "ch08.tpl.md").read_text(encoding="utf-8")
blocks = re.findall(r"```sql\n(.*?)```", tpl, flags=re.S)
MARK = "@@BLOCK_END@@"
script = "".join(f"{b}\n.print {MARK}\n" for b in blocks[:BLOCK])
r = subprocess.run(["duckdb", "-bail", ":memory:"], input=script, text=True, capture_output=True)
if r.returncode != 0:
    raise SystemExit(r.stderr)
parts = r.stdout.split(MARK + "\n")
print(parts[BLOCK - 1].strip("\n"))
