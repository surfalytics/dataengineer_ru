#!/usr/bin/env python3
"""Глава 9: data mesh score. Пять чисел складываем, по сумме читаем вывод.
Вопросы и пороги (15 и 30) из главы. Компании ниже выдуманы нами.
Запуск: python3 -I scripts/data-quality-fundamentals-code/ch09_mesh_score.py"""


def mesh_score(sources, team, domains, bottleneck, governance):
    """sources: число источников данных; team: аналитики + инженеры + продакты;
    domains: команды-потребители + продукты + data-фичи; bottleneck и governance: от 1 до 10."""
    assert 1 <= bottleneck <= 10 and 1 <= governance <= 10
    return sources + team + domains + bottleneck + governance


def verdict(score):
    # в книге границы 15 и 30 попадают в два диапазона сразу; берём: до 15 включительно, от 30 включительно
    if score <= 15:
        return "data mesh, скорее всего, не нужен"
    if score < 30:
        return "взять практики data mesh, чтобы потом проще мигрировать"
    return "data mesh в зоне пользы (sweet spot)"


companies = {
    "небольшой стартап": dict(sources=4, team=2, domains=3, bottleneck=2, governance=2),
    "растущий продукт": dict(sources=8, team=5, domains=6, bottleneck=5, governance=4),
    "крупная компания": dict(sources=40, team=25, domains=30, bottleneck=8, governance=9),
}
for name, answers in companies.items():
    s = mesh_score(**answers)
    print(f"{name:18} score = {s:3} -> {verdict(s)}")
