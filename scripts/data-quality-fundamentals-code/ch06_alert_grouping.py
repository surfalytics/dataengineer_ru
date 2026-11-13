"""Глава 6, кейс PagerDuty, практика 2 и 3: подавление шума и группировка алертов.
Алерты одного пайплайна, которые пришли подряд, считаем одним инцидентом."""
WINDOW = 30  # минут: алерты ближе этого окна попадают в один инцидент

ALERTS = [  # (минута от начала дня, пайплайн, тип алерта)
    (5,   "orders_dag",  "freshness"),
    (9,   "orders_dag",  "volume"),
    (12,  "orders_dag",  "schema"),
    (14,  "orders_dag",  "volume"),
    (40,  "finance_dag", "freshness"),
    (55,  "orders_dag",  "freshness"),
    (300, "orders_dag",  "volume"),
]
CRITICAL = {"finance_dag"}  # критичные данные: отчётность, финансы


def group(alerts):
    incidents = []
    last_seen = {}  # пайплайн -> индекс открытого инцидента
    for minute, pipe, kind in sorted(alerts):
        i = last_seen.get(pipe)
        if i is not None and minute - incidents[i]["last"] <= WINDOW:
            incidents[i]["alerts"].append(kind)
            incidents[i]["last"] = minute
        else:
            incidents.append({"pipe": pipe, "first": minute, "last": minute, "alerts": [kind]})
            last_seen[pipe] = len(incidents) - 1
    return incidents


incidents = group(ALERTS)
print(f"алертов: {len(ALERTS)}, инцидентов после группировки: {len(incidents)}")
for n, inc in enumerate(incidents, 1):
    route = "эскалация: on-call + BI-команда" if inc["pipe"] in CRITICAL else "on-call владельца пайплайна"
    kinds = ", ".join(inc["alerts"])
    print(f"#{n} {inc['pipe']:<12} с минуты {inc['first']:>3}, алертов {len(inc['alerts'])} ({kinds}) -> {route}")
