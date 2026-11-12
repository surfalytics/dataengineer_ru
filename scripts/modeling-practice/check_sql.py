"""Проверяет SQL в уроках курса «Базовый минимум Dimensional Modeling».

Запуск из корня репозитория:
    python3 scripts/modeling-practice/check_sql.py          # только ошибки
    python3 scripts/modeling-practice/check_sql.py --show   # печатает результат каждого блока

Что делает:
1. Распаковывает public/assets/practice/modeling-practice.tar.gz во временную папку.
2. Берёт все блоки ```sql из уроков в порядке sidebar.order.
3. Запускает их по очереди в одной базе modeling.duckdb (как ученик).
Нужен duckdb CLI в PATH. Код выхода 1, если хоть один блок упал.
"""

import re
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

DOCS = Path("src/content/docs/practice/modeling")
ARCHIVE = Path("public/assets/practice/modeling-practice.tar.gz").resolve()
FENCE = re.compile(r"^```sql\n(.*?)^```", re.S | re.M)
ORDER = re.compile(r"^\s+order:\s*(\d+)", re.M)

show = "--show" in sys.argv
only = [a for a in sys.argv[1:] if not a.startswith("--")]

lessons = sorted(DOCS.glob("*.md*"), key=lambda p: int(ORDER.search(p.read_text()).group(1)))
bad = 0
with tempfile.TemporaryDirectory() as tmp:
    with tarfile.open(ARCHIVE) as tar:
        tar.extractall(tmp, filter="data")
    work = Path(tmp) / "modeling-practice"
    for lesson in lessons:
        blocks = FENCE.findall(lesson.read_text(encoding="utf-8"))
        print(f"== {lesson.name} ({len(blocks)} blocks)")
        for i, sql in enumerate(blocks, 1):
            r = subprocess.run(["duckdb", "-bail", "modeling.duckdb"], input=sql, text=True,
                               capture_output=True, cwd=work)
            if r.returncode != 0 or r.stderr.strip():
                bad += 1
                print(f"FAIL {lesson.name} block {i}\n{sql.strip()[:400]}\n--> {r.stderr.strip()[:800]}")
            elif show and (not only or lesson.stem in only):
                print(f"-- block {i}\n{r.stdout.rstrip()}")
print("OK" if not bad else f"{bad} failed")
sys.exit(1 if bad else 0)
