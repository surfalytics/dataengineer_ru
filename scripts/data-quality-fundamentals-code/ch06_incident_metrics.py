"""Глава 6, SLI для инцидентов: N, TTD и TTR.
Журнал инцидентов с тремя временными метками: началось, обнаружили, исправили."""
from datetime import datetime
from statistics import median

INCIDENTS = [  # (таблица, началось, обнаружили, исправили)
    ("orders",    "2026-03-02 02:00", "2026-03-02 02:20", "2026-03-02 05:00"),
    ("orders",    "2026-03-09 02:00", "2026-03-09 02:10", "2026-03-09 03:30"),
    ("customers", "2026-03-04 10:00", "2026-03-06 09:00", "2026-03-06 15:00"),
    ("payments",  "2026-03-11 23:00", "2026-03-12 07:00", "2026-03-12 11:00"),
    ("payments",  "2026-03-20 06:00", "2026-03-20 06:05", "2026-03-20 07:00"),
]


def hours(a, b):
    fmt = "%Y-%m-%d %H:%M"
    return (datetime.strptime(b, fmt) - datetime.strptime(a, fmt)).total_seconds() / 3600


by_table = {}
for table, start, found, fixed in INCIDENTS:
    by_table.setdefault(table, []).append((hours(start, found), hours(found, fixed)))

print(f"{'таблица':<10}{'N':>3}{'TTD, ч':>9}{'TTR, ч':>9}")
for table, rows in by_table.items():
    ttd = median(r[0] for r in rows)
    ttr = median(r[1] for r in rows)
    print(f"{table:<10}{len(rows):>3}{ttd:>9.1f}{ttr:>9.1f}")

all_ttd = [hours(s, f) for _, s, f, _ in INCIDENTS]
all_ttr = [hours(f, x) for _, _, f, x in INCIDENTS]
print(f"\nвсего инцидентов N = {len(INCIDENTS)}")
print(f"медиана TTD = {median(all_ttd):.1f} ч, медиана TTR = {median(all_ttr):.1f} ч")
worst = max(INCIDENTS, key=lambda r: hours(r[1], r[2]))
print(f"худший TTD = {max(all_ttd):.1f} ч (таблица {worst[0]}: тихая ошибка жила почти два дня)")
