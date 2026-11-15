#!/usr/bin/env python3
"""Chapter 14 (what stage are you at) diagrams. Usage: ch14_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

# Fig 14-1: why the five stages go in this order
D["ch14-stage-order"] = dict(items=[
    T("Этап", 0, -50, 22, "#1971c2"),
    T("Почему он стоит здесь", 380, -50, 22, "#495057"),
    N("emp", "1. Empathy", 0, 0, "p", 260, 100),
    N("sti", "2. Stickiness", 0, 170, "p", 260, 100),
    N("vir", "3. Virality", 0, 340, "p", 260, 100),
    N("rev", "4. Revenue", 0, 510, "g", 260, 100),
    N("sca", "5. Scale", 0, 680, "g", 260, 100),
    N("r1", "Найти проблему и решение дешевле всего:\nхватит чашки кофе с клиентом.\nСнимает главный риск: это кому-то нужно?", 380, 0, "n", 560, 100),
    N("r2", "Нравится ли продукт людям? Исправьте ошибки\nна малой лояльной аудитории,\nа не на всём рынке", 380, 170, "n", 560, 100),
    N("r3", "Рекомендации дают рост и подтверждают,\nчто продукт хорош. Virality усиливает\nбудущую рекламу", 380, 340, "n", 560, 100),
    N("r4", "Готовы ли люди платить столько,\nчтобы покрыть работу компании\nи платное привлечение?", 380, 510, "n", 560, 100),
    N("r5", "Нужны каналы и партнёры, чтобы окупить\nпродажи и дистрибуцию и вырасти\nиз нишевого игрока в крупную компанию", 380, 680, "n", 560, 100),
], edges=[E("emp", "sti"), E("sti", "vir"), E("vir", "rev"), E("rev", "sca"),
          E("emp", "r1", dashed=True, head=False), E("sti", "r2", dashed=True, head=False),
          E("vir", "r3", dashed=True, head=False), E("rev", "r4", dashed=True, head=False),
          E("sca", "r5", dashed=True, head=False)])

# ch14-three-engines removed: same idea as ch05-growth-engines (chapter 5).

if __name__ == "__main__":
    run_all(D)
