"""Проверяет, что все SQL-блоки в уроках выполняются в учебной базе DuckDB.

Запуск: python3 check_lessons.py <файл базы .duckdb> <папка или файлы .md/.mdx>...
Блок пропускается, если его первая строка содержит «-- ошибка» (пример ошибки)
или «-- не запускать» (например, синтаксис другой базы).
"""
import pathlib
import re
import subprocess
import sys

SKIP = ("-- ошибка", "-- не запускать")


def blocks(path: pathlib.Path):
    text = path.read_text(encoding="utf-8")
    for m in re.finditer(r"```sql\n(.*?)```", text, re.S):
        line = text.count("\n", 0, m.start()) + 1
        yield line, m.group(1)


def main() -> int:
    db, targets = sys.argv[1], sys.argv[2:]
    files = []
    for t in targets:
        p = pathlib.Path(t)
        files += sorted(p.rglob("*.md*")) if p.is_dir() else [p]
    total = failed = skipped = 0
    for f in files:
        for line, sql in blocks(f):
            first = sql.strip().split("\n", 1)[0]
            if any(s in first for s in SKIP):
                skipped += 1
                continue
            total += 1
            # LIMIT вывода: нам важна только ошибка, не результат.
            r = subprocess.run(["duckdb", "-readonly", "-csv", db], input=sql, capture_output=True, text=True)
            err = r.stderr.strip()
            if r.returncode != 0 or "Error" in err:
                failed += 1
                print(f"FAIL {f}:{line}\n  {err.splitlines()[0] if err else 'exit ' + str(r.returncode)}")
    print(f"checked {total}, failed {failed}, skipped {skipped}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
