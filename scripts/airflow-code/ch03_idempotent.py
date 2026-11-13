"""Глава 3: идемпотентность. Три запуска одной task: дописывать в общий файл и перезаписывать partition.
Чистый Python, Airflow не нужен."""
import tempfile
from pathlib import Path

events = ["event1", "event2", "event3"]  # события одного дня
folder = Path(tempfile.mkdtemp())
shared = folder / "events.json"
partition = folder / "events-2025-01-01.json"

for attempt in range(1, 4):
    with shared.open("a") as f:  # плохо: каждый повтор дописывает те же события
        f.write("\n".join(events) + "\n")
    partition.write_text("\n".join(events) + "\n")  # хорошо: повтор перезаписывает файл
    print(f"попытка {attempt}: общий файл {len(shared.read_text().splitlines())} строк, partition {len(partition.read_text().splitlines())} строк")
