#!/usr/bin/env python3
"""Собирает страницу главы из шаблона: подставляет код скриптов и их настоящий вывод.
Маркеры в шаблоне (каждый на отдельной строке):
  {{code: ch03_example.py}}  -> сворачиваемый блок <details> с полным кодом скрипта
  {{out: ch03_example.py}}   -> блок ```text с выводом скрипта (скрипт запускается сейчас)
Запуск: python3 scripts/data-quality-fundamentals-code/embed.py <template.md> <result.md>
Так код и вывод на странице всегда совпадают с файлами и с настоящим запуском."""
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def run(name):
    r = subprocess.run([sys.executable, "-I", str(HERE / name)], capture_output=True, text=True, cwd=ROOT, timeout=300)
    if r.returncode != 0:
        raise SystemExit(f"{name} failed:\n{r.stderr}")
    return r.stdout.rstrip("\n")


def sub(m):
    kind, name = m.group(1), m.group(2).strip()
    if kind == "code":
        body = (HERE / name).read_text(encoding="utf-8").rstrip("\n")
        return f"<details>\n<summary>Код: {name}</summary>\n\n```python\n{body}\n```\n\n</details>"
    return f"```text\n{run(name)}\n```"


tpl = Path(sys.argv[1]).read_text(encoding="utf-8")
Path(sys.argv[2]).write_text(re.sub(r"^\{\{(code|out):([^}]+)\}\}$", sub, tpl, flags=re.M), encoding="utf-8")
print("written", sys.argv[2])
