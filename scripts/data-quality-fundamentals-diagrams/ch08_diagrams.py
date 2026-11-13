#!/usr/bin/env python3
"""Chapter 8 (democratizing data quality) diagrams. Usage: ch08_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

# own: chapter map (main diagram)
D["ch08-democratizing-map"] = dict(items=[
    N("goal", "Доверие к данным\nво всей компании", 470, 0, "g", 380, 100),
    N("p1", "Данные\nкак продукт", 0, 190, "p", 300, 90),
    N("p2", "Владение и\nсертификация", 340, 190, "pu", 300, 90),
    N("p3", "Грамотность\nи знания", 680, 190, "y", 300, 90),
    N("p4", "Governance и\nкомплаенс", 1020, 190, "db", 300, 90),
    N("d1", "Владелец, SLA, KPI,\nself-serve, зрелость\nнадёжности, hub\nand spoke, build/buy", 0, 360, "n", 300, 150),
    N("d2", "Роли и RACI,\nblast radius,\n7 шагов data\ncertification", 340, 360, "n", 300, 150),
    N("d3", "Head of Data\nLiteracy, документация,\nкаталоги и\nописание метаданных", 680, 360, "n", 300, 150),
    N("d4", "Каталог данных,\nlineage, политики\nдоступа, культура,\nстратегия качества", 1020, 360, "n", 300, 150),
], edges=[E("goal", "p1"), E("goal", "p2"), E("goal", "p3"), E("goal", "p4"),
          E("p1", "d1"), E("p2", "d2"), E("p3", "d3"), E("p4", "d4")])

# Fig 8-1: reliability maturity curve
D["ch08-maturity-curve"] = dict(items=[
    T("Модель зрелости надёжности данных: четыре стадии", 0, -50, 22, "#1971c2"),
    N("s1", "Reactive", 0, 0, "r", 270, 80),
    N("s2", "Proactive", 330, 0, "y", 270, 80),
    N("s3", "Automated", 660, 0, "p", 270, 80),
    N("s4", "Scalable", 990, 0, "g", 270, 80),
    N("d1", "Тушение пожаров.\nБольшая часть времени\nуходит на разбор\nинцидентов", 0, 160, "n", 270, 150),
    N("d2", "Ручные проверки\nи свои QA-запросы:\nrow count, свежесть.\nАлерты в Slack и почте", 330, 160, "n", 270, 150),
    N("d3", "Проверки по\nрасписанию, дашборды\nздоровья данных,\nконтроль схемы\nпри ingestion", 660, 160, "n", 270, 150),
    N("d4", "Staging, повторно\nиспользуемые проверки,\nhard и soft alerts,\nanomaly detection\nдля всех метрик", 990, 160, "n", 270, 150),
], edges=[E("s1", "s2"), E("s2", "s3"), E("s3", "s4"),
          E("s1", "d1", dashed=True), E("s2", "d2", dashed=True), E("s3", "d3", dashed=True), E("s4", "d4", dashed=True)])

# Fig 8-4: blast radius
D["ch08-blast-radius"] = dict(items=[
    T("Blast radius: чем дальше от источника, тем больше ущерб", 0, -50, 22, "#e03131"),
    N("w1", "Data engineering\nплатформа:\nwarehouse, lake, ETL", 0, 0, "g", 260, 110),
    N("w2", "Analytics и\ndata science:\nBI, модели", 310, 0, "y", 260, 110),
    N("w3", "Приложения для\nклиентов: рекомендации,\nперсонализация", 620, 0, "q", 260, 110),
    N("w4", "Сотрудники:\nрешения, доверие\nк данным", 930, 0, "r", 260, 110),
    N("w5", "Публика:\nСМИ, инвесторы,\nрегуляторы", 1240, 0, "r", 260, 110),
    N("i1", "Под контролем", 0, 170, "n", 260, 70),
    N("i2", "Раздражает", 310, 170, "n", 260, 70),
    N("i3", "Потеря выручки", 620, 170, "n", 260, 70),
    N("i4", "Вредит компании\nи карьере", 930, 170, "n", 260, 90),
    N("i5", "Экзистенциальный\nи юридический риск", 1240, 170, "n", 260, 90),
], edges=[E("w1", "w2"), E("w2", "w3"), E("w3", "w4"), E("w4", "w5"),
          E("w1", "i1", dashed=True), E("w2", "i2", dashed=True), E("w3", "i3", dashed=True),
          E("w4", "i4", dashed=True), E("w5", "i5", dashed=True)])

# own: 7 steps of data certification
D["ch08-certification-steps"] = dict(items=[
    N("c1", "1. Observability:\nмониторы и alerts,\nбазовый уровень", 0, 0, "p", 270, 120),
    N("c2", "2. Владельцы:\nответственный на\nкаждом слое", 330, 0, "p", 270, 120),
    N("c3", "3. Что значит «хорошо»:\nvolume, freshness,\ndistribution, schema", 660, 0, "p", 270, 120),
    N("c4", "4. SLA, SLO, SLI\nдля важнейших\nнаборов данных", 990, 0, "p", 270, 120),
    N("c5", "5. Коммуникации и\nуправление инцидентами:\nSlack, PagerDuty", 990, 200, "pu", 270, 120),
    N("c6", "6. Тег certified\nв каталоге или\nв data discovery", 660, 200, "pu", 270, 120),
    N("c7", "7. Обучение команды\nи потребителей\nданных", 330, 200, "pu", 270, 120),
    N("ok", "Certified: таблице\nможно доверять\n(tier: bronze, silver, gold)", 0, 200, "g", 270, 120),
], edges=[E("c1", "c2"), E("c2", "c3"), E("c3", "c4"), E("c4", "c5"), E("c5", "c6"), E("c6", "c7"), E("c7", "ok")])

if __name__ == "__main__":
    run_all(D)
