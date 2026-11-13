#!/usr/bin/env python3
"""Глава 7 (Airflow): новые диаграммы. Старую (ch07-triggers) делает specs/ch07.py.
Usage: python3 scripts/airflow-diagrams/ch07_diagrams.py [name ...]"""
from excb import N, E, Z, T, run_all

D = {}
GRAY = "#495057"

# ---------- Fig 7.2-7.4: запуск в 02:00 или sensors с начала окна ----------
rows = [("Супермаркет 1", "16:30", "9,5 ч"), ("Супермаркет 2", "18:45", "7,25 ч"),
        ("Супермаркет 3", "21:15", "4,75 ч"), ("Супермаркет 4", "00:30", "1,5 ч")]
items = [T("Данные приходят в разное время. Когда их начать обрабатывать?", 0, -50, 22, "#1971c2"),
         T("Запуск DAG в 02:00", 250, 0, 22, "#e03131"), T("Sensors с 15:00", 880, 0, 22, "#2f9e44")]
for i, (name, t, wait) in enumerate(rows):
    y = 50 + i * 110
    items.append(N(f"n{i}", f"{name}\nданные в {t}", 0, y, "p", 230, 90))
    items.append(N(f"a{i}", f"ждут {wait}, обработка в 02:00", 270, y, "r", 400, 90))
    items.append(N(f"b{i}", "обработка сразу после прихода", 760, y, "g", 440, 90))
items.append(T("Слева данные лежат без дела. Справа sensor видит файл и пускает ветку дальше.", 0, 500, 20, GRAY))
D["ch07-wait-timeline"] = dict(items=items, edges=[])

# ---------- Fig 7.8-7.10: poke, reschedule, deferrable ----------
items = [T("Что делает worker slot, пока task ждёт событие", 0, -50, 22, "#1971c2")]
items += [T("mode=\"poke\"", 0, 20, 22, "#e03131"),
          N("p1", "слот занят: проверка", 260, 0, "r", 250, 80), N("p2", "слот занят: пауза", 530, 0, "r", 250, 80),
          N("p3", "слот занят: проверка", 800, 0, "r", 250, 80), N("p4", "слот занят: пауза", 1070, 0, "r", 250, 80)]
items += [T("mode=\"reschedule\"", 0, 150, 22, "#f08c00"),
          N("r1", "проверка", 260, 130, "y", 250, 80), N("r2", "слот свободен", 530, 130, "n", 250, 80),
          N("r3", "проверка", 800, 130, "y", 250, 80), N("r4", "слот свободен", 1070, 130, "n", 250, 80)]
items += [T("deferrable", 0, 280, 22, "#2f9e44"),
          N("d1", "старт на worker", 260, 260, "g", 250, 80), N("d2", "ждёт triggerer (asyncio)\nслот свободен", 530, 260, "pu", 520, 80),
          N("d3", "возврат на worker", 1070, 260, "g", 250, 80)]
items.append(T("Слоты ограничены (16 tasks на DAG по умолчанию). Sensor в mode=poke съедает слот на всё ожидание.", 0, 380, 20, GRAY))
D["ch07-slots"] = dict(items=items, edges=[])

# ---------- Fig 7.12: сообщение в Kafka запускает DAG ----------
D["ch07-kafka-asset"] = dict(items=[
    T("Как сообщение в очереди запускает DAG в Airflow 3", 0, -50, 22, "#1971c2"),
    N("src", "Поставщик\nпишет сообщение «готово»", 0, 0, "q", 270, 100),
    N("topic", "Kafka topic\nuploads", 340, 0, "n", 230, 100),
    N("trg", "MessageQueueTrigger\n(работает в triggerer)", 640, 0, "pu", 300, 100),
    N("asset", "Asset\n+ AssetWatcher", 1010, 0, "y", 230, 100),
    N("dag", "DAG run\nschedule=[asset]", 1010, 220, "g", 230, 100),
    N("fn", "apply_function:\nTrue = запускать", 640, 220, "p", 300, 100),
    T("Если apply_function вернула False, сообщение пропускается и DAG не стартует.", 0, 360, 20, GRAY),
    T("Пауза до старта возможна: consumer читает очередь с фиксированным интервалом.", 0, 395, 20, GRAY),
], edges=[E("src", "topic"), E("topic", "trg", "читает"), E("trg", "fn", "каждое сообщение"),
          E("fn", "asset", "True", dashed=True), E("asset", "dag", "событие Asset")])

if __name__ == "__main__":
    run_all(D)
