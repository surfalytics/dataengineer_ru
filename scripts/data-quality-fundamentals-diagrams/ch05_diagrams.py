#!/usr/bin/env python3
"""Chapter 5 (architecting for data reliability) diagrams. Usage: ch05_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

# own: main map of the chapter - three stages and three prongs
D["ch05-reliability-map"] = dict(items=[
    T("Где защищаем данные", 0, -50, 22, "#1971c2"),
    N("s1", "Загрузка\n(ingestion)", 0, 0, "p", 330, 90),
    N("s2", "Внутри пайплайна\n(in production)", 420, 0, "p", 330, 90),
    N("s3", "На выходе\n(analytics layer)", 840, 0, "p", 330, 90),
    N("d1", "Очистка, обогащение\nи тесты: unique, not_null,\nдиапазон, свежесть, объём", 0, 170, "g", 330, 130),
    N("d2", "Data observability:\nfreshness, distribution,\nvolume, schema, lineage", 420, 170, "g", 330, 130),
    N("d3", "Дашборд надёжности,\nSLA, SLI, SLO,\nTTD и TTR", 840, 170, "g", 330, 130),
    T("Что для этого нужно (три направления)", 0, 360, 22, "#9c36b5"),
    N("p1", "1. Процессы из DevOps:\nтесты и observability\nс самого начала", 0, 410, "pu", 330, 120),
    N("p2", "2. Устойчивая\nплатформа данных:\nшесть слоёв", 420, 410, "pu", 330, 120),
    N("p3", "3. SLA, SLI, SLO,\nс которыми согласны\nвсе стороны", 840, 410, "pu", 330, 120),
    N("res", "Надёжные данные\nи доверие к ним", 1250, 410, "y", 300, 120),
], edges=[E("s1", "s2"), E("s2", "s3"), E("s1", "d1", dashed=True), E("s2", "d2", dashed=True),
          E("s3", "d3", dashed=True), E("p1", "p2"), E("p2", "p3"), E("p3", "res")])

# Fig 5-1 + 5-4: data platform layers
D["ch05-platform-layers"] = dict(items=[
    T("Поток данных через платформу", 0, -50, 22, "#1971c2"),
    N("src", "Источники:\nоперационные системы,\nвнешние данные", 0, 0, "n", 240, 110),
    N("ing", "Ingestion\nextract и load,\nETL или ELT", 300, 0, "p", 240, 110),
    N("sto", "Storage и processing\nwarehouse, lake,\nlakehouse", 600, 0, "db", 240, 110),
    N("tra", "Transformation\nи modeling\nтаблицы и связи", 900, 0, "pu", 240, 110),
    N("bi", "BI и analytics\nдашборды, графики,\ndata storytelling", 1200, 0, "g", 240, 110),
    Z("Сквозные слои: работают на всех этапах сразу", 300, 210, 1140, 210),
    N("disc", "Discovery и governance\nвидит текущее состояние:\nсвежесть, доступ, зависимости", 360, 280, "y", 480, 110),
    N("obs", "Observability\nfreshness, distribution, volume,\nschema, lineage", 900, 280, "r", 480, 110),
    T("Слои связаны между собой, а не лежат стопкой. Один инструмент может закрывать 2-3 слоя.", 0, 460, 20, "#495057"),
], edges=[E("src", "ing"), E("ing", "sto"), E("sto", "tra"), E("tra", "bi")])

# own: cost of data downtime
D["ch05-downtime-cost"] = dict(items=[
    T("Как проблема с данными превращается в деньги", 0, -50, 22, "#1971c2"),
    N("a", "Данные\nсломались", 0, 0, "r", 220, 90),
    N("b", "Заметили", 400, 0, "y", 220, 90),
    N("c", "Починили", 800, 0, "g", 220, 90),
    N("f1", "Формула 1\n(TTD + TTR) x цена часа\n= цена data downtime", 0, 190, "p", 440, 110),
    N("h", "Цена часа:\nвремя инженеров\n+ простой аналитиков\n+ вред для решений", 680, 175, "n", 360, 140),
    N("f2", "Формула 2\nlabor + compliance + opportunity\n= цена плохих данных за год", 0, 380, "pu", 520, 110),
    N("n", "labor: инженеры x зарплата x 30%\ncompliance: 4% годовой выручки\nopportunity: упущенная выручка", 800, 370, "y", 520, 130),
], edges=[E("a", "b", "TTD"), E("b", "c", "TTR"), E("f1", "h", "цена часа"), E("f2", "n", "из чего")])

# own: SLI -> SLO -> SLA with an example
D["ch05-sla-slo-sli"] = dict(items=[
    T("Три слова и один пример", 0, -50, 22, "#1971c2"),
    N("sli", "SLI\nизмеряемый показатель", 0, 0, "p", 330, 90),
    N("slo", "SLO\nцелевое значение для SLI", 500, 0, "g", 330, 90),
    N("sla", "SLA\nобещание потребителям\nи последствия нарушения", 1000, -10, "y", 360, 110),
    N("e1", "Пример: сколько часов\nпрошло с последнего\nобновления таблицы orders", 0, 170, "n", 330, 120),
    N("e2", "Пример: не больше\n10 часов, и так\nв 95% дней", 500, 170, "n", 330, 120),
    N("e3", "Пример: если нарушим,\nпервым делом разбор\nи отчёт для руководства", 1000, 170, "n", 360, 120),
    Z("Три шага команды данных", 0, 350, 1360, 230),
    N("st1", "Шаг 1. Defining\nопись данных, интервью\nс потребителями", 30, 410, "pu", 360, 110),
    N("st2", "Шаг 2. Measuring\nвыбор SLI: инциденты,\nчастота, распределение", 500, 410, "pu", 360, 110),
    N("st3", "Шаг 3. Tracking\nSLO, уровни тяжести,\nдашборд", 970, 410, "pu", 360, 110),
], edges=[E("sli", "slo", "цель"), E("slo", "sla", "обещание"),
          E("sli", "e1", dashed=True, head=False), E("slo", "e2", dashed=True, head=False),
          E("sla", "e3", dashed=True, head=False), E("st1", "st2"), E("st2", "st3")])

if __name__ == "__main__":
    run_all(D)
