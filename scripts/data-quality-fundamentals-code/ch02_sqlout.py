#!/usr/bin/env python3
"""Подставляет настоящий вывод DuckDB в шаблон главы 2.
В шаблоне после блока ```sql может идти строка {{sqlout}}. Тогда скрипт запускает все блоки sql
до этого места (одна сессия DuckDB) и вставляет вывод последнего блока как ```text.
Запуск: python3 scripts/data-quality-fundamentals-code/ch02_sqlout.py <шаблон> <результат>
Дальше результат идёт в embed.py (он подставляет вывод Python-скриптов)."""
import re
import subprocess
import sys

SEP = "@@SEP@@"
tpl = open(sys.argv[1], encoding="utf-8").read()
fence = re.compile(r"```sql\n(.*?)```", re.S)


def duck(script):
    r = subprocess.run(["duckdb", "-bail", ":memory:"], input=script, text=True, capture_output=True)
    if r.returncode != 0:
        raise SystemExit("duckdb error:\n" + r.stderr[:1500])
    return r.stdout


blocks = [(m.start(), m.end(), m.group(1)) for m in fence.finditer(tpl)]
out, pos = [], 0
for i, (s, e, body) in enumerate(blocks):
    out.append(tpl[pos:e])
    pos = e
    tail = tpl[e:].lstrip("\n")
    if tail.startswith("{{sqlout}}"):
        script = "".join(f".print {SEP}\n{b[2]}\n" for b in blocks[:i + 1])
        text = duck(script).split(SEP + "\n")[-1].rstrip("\n")
        out.append(f"\n\n```text\n{text}\n```")
        pos = tpl.index("{{sqlout}}", e) + len("{{sqlout}}")
out.append(tpl[pos:])
open(sys.argv[2], "w", encoding="utf-8").write("".join(out))
print("written", sys.argv[2])
