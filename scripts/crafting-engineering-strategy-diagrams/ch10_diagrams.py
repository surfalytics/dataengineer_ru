#!/usr/bin/env python3
"""Chapter 10 (operations) diagrams. Usage: ch10_diagrams.py [name ...]  (no args = all)"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from excb import N, E, Z, T, run_all

D = {}

# own: from policy to operational plan, with the six-factor rubric
fac = ["Measurability:\nизмеримость", "Adoption cost:\nцена внедрения", "Удобство\nдля пользователей",
       "Удобство для\nкоманды-провайдера", "Зависимость\nот власти", "Согласованность\nс культурой"]
items = [N("pol", "Политика", 0, 0, "p", 230, 100),
         N("cand", "Кандидаты в\nмеханизмы", 320, 0, "y", 230, 100),
         N("rub", "Оценка по\nшести факторам", 640, 0, "q", 230, 100),
         N("plan", "План внедрения:\nмеханизмы вместе", 960, 0, "g", 230, 100),
         N("rev", "Проверка с людьми\nи обзор через\n3 месяца", 1280, 0, "g", 230, 100)]
edges = [E("pol", "cand"), E("cand", "rub"), E("rub", "plan"), E("plan", "rev")]
for i, f in enumerate(fac):
    items.append(N(f"f{i}", f, i * 250, 260, "n", 230, 100))
    edges.append(E("rub", f"f{i}", dashed=True))
D["ch10-operational-plan"] = dict(items=items, edges=edges)

# own: Stripe cloud spend nudge + inspection
D["ch10-nudge-inspection"] = dict(items=[
    N("a", "Команда сама\nодобряет новые\nрасходы на облако", 0, 0, "p", 270, 120),
    N("b", "Расходы резко растут,\nкоманда этого\nне замечает", 380, 0, "r", 270, 120),
    N("c", "nudge: сообщение о росте,\nграфики и куда\nзадать вопрос", 760, 0, "g", 270, 120),
    N("d", "Команда видит\nпричину и сама\nисправляет", 1140, 0, "g", 270, 120),
    N("i", "inspection: Efficiency\nEngineering раз в месяц\nсмотрит всплески", 760, 260, "y", 270, 120),
], edges=[E("a", "b"), E("b", "c"), E("c", "d"), E("b", "i", dashed=True), E("i", "d", "пишет только\nтем, кто перерасходовал", dashed=True)])

if __name__ == "__main__":
    run_all(D)
