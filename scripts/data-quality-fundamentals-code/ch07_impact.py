"""Глава 7: что можно делать с lineage на уровне полей.
Берёт связи из ch07_lineage.py и отвечает на вопросы из книги:
  1. Сломалось поле в источнике. Какие поля дашбордов затронуты?
  2. Цифра в дашборде подозрительна. Какие поля источников её формируют?
  3. Какие колонки с PII доходят до дашбордов?
  4. Какие колонки никто не использует (data debt)?
Запуск: python3 -I scripts/data-quality-fundamentals-code/ch07_impact.py"""
import sys
from collections import defaultdict, deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ch07_lineage import SOURCES, build_edges  # noqa: E402

PII = [("raw.customers", "email")]

edges, _ = build_edges()
down, up = defaultdict(list), defaultdict(list)  # поле -> [(поле, вид связи)]
for dest_t, dest_c, src_t, src_c, kind in edges:
    down[(src_t, src_c)].append(((dest_t, dest_c), kind))
    up[(dest_t, dest_c)].append(((src_t, src_c), kind))


def reach(start, graph, only_select=False):
    """Обход графа в ширину. Возвращает все достижимые поля."""
    seen, queue = set(), deque([start])
    while queue:
        node = queue.popleft()
        for nxt, kind in graph[node]:
            if only_select and kind != "select":
                continue
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
    return seen


def show(fields):
    return ", ".join(f"{t}.{c}" for t, c in sorted(fields)) or "-"


def bi_only(fields):
    return {f for f in fields if f[0].startswith("bi.")}


print("== 1. Impact: поле источника сломалось")
for field in [("raw.orders", "amount"), ("raw.orders", "status")]:
    hit = bi_only(reach(field, down))
    values = bi_only(reach(field, down, only_select=True))
    print(f"{field[0]}.{field[1]}")
    print("  меняет значения в:", show(values))
    print("  меняет набор строк в:", show(hit - values))

print("\n== 2. Root cause: откуда берётся bi.revenue_dashboard.revenue")
target = ("bi.revenue_dashboard", "revenue")
roots = {f for f in reach(target, up) if f[0].startswith("raw.")}
values = {f for f in reach(target, up, only_select=True) if f[0].startswith("raw.")}
print("значение приходит из:", show(values))
print("набор строк задают:", show(roots - values))

print("\n== 3. PII: колонки с персональными данными доходят до дашбордов")
for field in PII:
    print(f"{field[0]}.{field[1]} ->", show(bi_only(reach(field, down))))

print("\n== 4. Data debt: колонки источников без потребителей")
unused = [(t, c) for t, cols in SOURCES.items() for c in cols if not down[(t, c)]]
print(show(unused))
