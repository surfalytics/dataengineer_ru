"""Глава 7: проверка без Airflow-сервера.
1) логика sensor-функции на временной папке;
2) арифметика sensor deadlock: сколько слотов занято по дням.
Запуск: python3 -I ch07_check_sensor.py."""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ch07_batch_ready import batch_is_ready  # noqa: E402

with tempfile.TemporaryDirectory() as tmp:
    folder = Path(tmp)
    print("пустая папка:", batch_is_ready(folder))
    (folder / "part-1.csv").write_text("a,b\n")
    print("данные есть, маркера нет:", batch_is_ready(folder))
    (folder / "_DONE").write_text("")
    print("данные и маркер:", batch_is_ready(folder))

# Один партнёр не присылает данные. Sensor в mode="poke" живёт до timeout (7 дней).
LIMIT = 16  # max_active_tasks по умолчанию
waiting_per_day = 3  # три партнёра из четырёх молчат
print("\nДень | занято слотов sensors")
for day in range(1, 8):
    busy = min(day * waiting_per_day, LIMIT)
    note = "  <- лимит, новые tasks не стартуют" if busy == LIMIT else ""
    print(f"{day:>4} | {busy}{note}")
