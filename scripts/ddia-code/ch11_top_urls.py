#!/usr/bin/env python3
"""DDIA2, глава 11: топ-5 страниц по логу веб-сервера двумя способами.

1. Цепочка Unix-команд: awk | sort | uniq -c | sort -r -n | head (сортировка).
2. Программа на Python со словарём счётчиков (агрегация в памяти).

Лог генерируется здесь же (фиксированный seed), файлы скачивать не нужно.
Запуск: python3 -I scripts/ddia-code/ch11_top_urls.py
"""
import random
import subprocess
import tempfile
from collections import defaultdict
from pathlib import Path

URLS = ["/", "/favicon.ico", "/css/typography.css", "/blog/kafka.html",
        "/blog/spark.html", "/blog/duckdb.html", "/about.html", "/rss.xml"]
WEIGHTS = [14, 30, 9, 21, 6, 17, 2, 4]


def make_log(path: Path, lines: int = 20_000, seed: int = 42) -> None:
    """Пишет лог в формате NGINX: URL стоит в 7-м поле строки."""
    rnd = random.Random(seed)
    with path.open("w") as f:
        for i in range(lines):
            ip = f"10.0.{rnd.randint(0, 9)}.{rnd.randint(1, 254)}"
            url = rnd.choices(URLS, WEIGHTS)[0]
            sec = i % 60
            f.write(f'{ip} - - [27/Jun/2025:17:55:{sec:02d} +0000] "GET {url} HTTP/1.1" '
                    f'200 3377 "-" "Mozilla/5.0"\n')


def top5_python(path: Path) -> list[str]:
    counts = defaultdict(int)              # URL -> сколько раз встретился
    with path.open() as f:
        for line in f:
            url = line.split()[6]          # 7-е поле, индекс 6
            counts[url] += 1
    top5 = sorted(((c, u) for u, c in counts.items()), reverse=True)[:5]
    return [f"{c} {u}" for c, u in top5]


def top5_unix(path: Path) -> list[str]:
    cmd = f"awk '{{print $7}}' {path} | sort | uniq -c | sort -r -n | head -n 5"
    out = subprocess.run(["bash", "-c", cmd], capture_output=True, text=True, check=True,
                         env={"LC_ALL": "C", "PATH": "/usr/bin:/bin"}).stdout
    return [" ".join(line.split()) for line in out.splitlines()]


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as d:
        log = Path(d) / "access.log"
        make_log(log)
        py, unix = top5_python(log), top5_unix(log)
    print("Unix pipeline:")
    print("\n".join(unix))
    print("Python:")
    print("\n".join(py))
    print("Совпадает:", py == unix)
