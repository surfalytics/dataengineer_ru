"""Глава 5: идемпотентная запись page views (sqlite3, без внешних сервисов).
Повторный запуск за тот же интервал: сначала без primary key, потом с upsert."""
import sqlite3

counts = {"Google": 399, "Amazon": 17, "Apple": 35}
hour = "2024-01-18T02:00:00"

db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE plain (pagename TEXT, pageviewcount INT, datetime TEXT)")
db.execute("CREATE TABLE safe (pagename TEXT, pageviewcount INT, datetime TEXT, PRIMARY KEY (pagename, datetime))")

for run in (1, 2):  # второй run это повторный запуск того же интервала
    for page, n in counts.items():
        db.execute("INSERT INTO plain VALUES (?, ?, ?)", (page, n, hour))
        db.execute(
            "INSERT INTO safe VALUES (?, ?, ?) ON CONFLICT (pagename, datetime) "
            "DO UPDATE SET pageviewcount = excluded.pageviewcount",
            (page, n, hour),
        )
    print(f"после run {run}: plain={db.execute('SELECT count(*) FROM plain').fetchone()[0]} строк, "
          f"safe={db.execute('SELECT count(*) FROM safe').fetchone()[0]} строк")
