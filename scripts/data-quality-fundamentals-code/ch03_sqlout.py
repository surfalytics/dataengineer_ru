#!/usr/bin/env python3
"""Подставляет настоящий вывод DuckDB на страницу главы 3.
Маркер {{sqlout}} на отдельной строке заменяется выводом ближайшего блока ```sql выше него.
Все блоки ```sql выполняются по порядку в одной сессии, как на странице.
Запуск (после embed.py): python3 scripts/data-quality-fundamentals-code/ch03_sqlout.py <page.md>"""
import re
import subprocess
import sys
from pathlib import Path

page = Path(sys.argv[1])
text = page.read_text(encoding="utf-8")
fence = re.compile(r"```sql\n(.*?)```", re.S)
blocks = fence.findall(text)
script = "".join(f"{b}\n.print @@END{i}@@\n" for i, b in enumerate(blocks))
r = subprocess.run(["duckdb", "-bail", ":memory:"], input=script, text=True, capture_output=True)
if r.returncode != 0:
    raise SystemExit("duckdb failed:\n" + r.stderr)
outs, rest = {}, r.stdout
for i in range(len(blocks)):
    head, _, rest = rest.partition(f"@@END{i}@@\n")
    outs[i] = head.rstrip("\n")

pieces, pos, idx = [], 0, 0
for m in re.finditer(r"^\{\{sqlout\}\}$", text, flags=re.M):
    idx = len(fence.findall(text[:m.start()])) - 1  # номер ближайшего блока sql выше маркера
    pieces.append(text[pos:m.start()])
    pieces.append(f"```text\n{outs[idx]}\n```")
    pos = m.end()
pieces.append(text[pos:])
page.write_text("".join(pieces), encoding="utf-8")
print("sql outputs inserted into", page)
