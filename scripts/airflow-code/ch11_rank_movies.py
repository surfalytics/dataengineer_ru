#!/usr/bin/env python
"""CLI-скрипт для задачи в контейнере: считает рейтинг фильмов из JSON с оценками.
Так выглядит код, который кладут в image (глава 11). click==8.5.1."""
import csv
import json
from collections import defaultdict
from pathlib import Path

import click


@click.command()
@click.option("--input_path", type=click.Path(exists=True), required=True, help="JSON с оценками.")
@click.option("--output_path", type=click.Path(), required=True, help="CSV с рейтингом.")
@click.option("--top", type=int, default=3, show_default=True, help="Сколько фильмов оставить.")
def main(input_path, output_path, top):
    """Считает средний рейтинг фильмов."""
    ratings = json.loads(Path(input_path).read_text())
    by_movie = defaultdict(list)
    for r in ratings:
        by_movie[r["movieId"]].append(r["rating"])
    rows = [(m, round(sum(v) / len(v), 2), len(v)) for m, v in by_movie.items()]
    rows.sort(key=lambda x: (-x[1], -x[2], x[0]))
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)  # папка может быть новым volume
    with out.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["movieId", "avg_rating", "num_ratings"])
        w.writerows(rows[:top])
    click.echo(f"Фильмов в рейтинге: {min(top, len(rows))}. Файл: {out.name}")


if __name__ == "__main__":
    main()
