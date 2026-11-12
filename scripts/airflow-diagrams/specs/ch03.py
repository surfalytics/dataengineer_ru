from lib import N, E, Z, T

D = {}

D["ch03-trigger-vs-interval"] = dict(items=[
    Z("Trigger timetable (CronTriggerTimetable)", 0, 0, 950, 200),
    N("t1", "Момент времени\n00:00", 30, 70, "n"),
    N("t2", "Run стартует\nсразу", 350, 70, "p"),
    N("t3", "Есть logical_date", 670, 70, "g"),
    Z("Data interval timetable (CronDataIntervalTimetable)", 0, 260, 950, 200),
    N("i1", "Интервал\n01-01 .. 01-02", 30, 330, "n"),
    N("i2", "Run стартует\nв конце интервала", 350, 330, "p"),
    N("i3", "data_interval_start\ndata_interval_end", 670, 330, "g"),
], edges=[
    E("t1", "t2"), E("t2", "t3"), E("i1", "i2"), E("i2", "i3"),
])

D["ch03-incremental-partitions"] = dict(items=[
    N("d1", "Интервал\n2025-01-01", 0, 0, "n"),
    N("e1", "events/\n2025-01-01.json", 500, 0, "db"),
    N("s1", "stats/\n2025-01-01.csv", 1000, 0, "db"),
    N("d2", "Интервал\n2025-01-02", 0, 150, "n"),
    N("e2", "events/\n2025-01-02.json", 500, 150, "db"),
    N("s2", "stats/\n2025-01-02.csv", 1000, 150, "db"),
    N("d3", "Интервал\n2025-01-03", 0, 300, "n"),
    N("e3", "events/\n2025-01-03.json", 500, 300, "db"),
    N("s3", "stats/\n2025-01-03.csv", 1000, 300, "db"),
], edges=[
    E("d1", "e1", "fetch_events"), E("e1", "s1", "calculate_stats"),
    E("d2", "e2", "fetch_events"), E("e2", "s2", "calculate_stats"),
    E("d3", "e3", "fetch_events"), E("e3", "s3", "calculate_stats"),
])
