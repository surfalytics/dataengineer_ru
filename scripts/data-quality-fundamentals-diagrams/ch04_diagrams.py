#!/usr/bin/env python3
"""Chapter 4 (monitoring and anomaly detection) diagrams. Usage: ch04_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

# Fig 4-1 (own version) + chapter map: two kinds of problems, what covers them, what a monitor watches
D["ch04-monitoring-map"] = dict(items=[
    N("a", "Known unknowns\nпроблемы, которые можно\nпредсказать: null, схема,\nсвежесть", 0, 0, "p", 340, 130),
    N("t", "Тесты и\ncircuit breakers", 430, 15, "p", 260, 100),
    N("b", "Unknown unknowns\nпроблемы, которых не ждали:\nJSON-схема с 6 колонками\nстала 600, дрейф данных", 0, 230, "r", 340, 130),
    N("m", "Мониторинг и\nanomaly detection", 430, 245, "pu", 260, 100),
    T("Тесты ловят то, что вы предвидели.\nМониторинг ловит остальное.", 800, 250, 20, "#e03131"),
    Z("Пять столпов", -20, 470, 1410, 260),
    N("p1", "Freshness:\nдней с последнего\nобновления", 0, 570, "g", 250, 120),
    N("p2", "Volume:\nсколько строк\nпришло за день", 280, 570, "g", 250, 120),
    N("p3", "Distribution:\nдоля null, среднее,\nдоля нулей", 560, 570, "g", 250, 120),
    N("p4", "Schema:\nсписок колонок\nпо дням", 840, 570, "g", 250, 120),
    N("p5", "Lineage:\nкто выше и ниже,\nконтекст причины", 1120, 570, "g", 250, 120),
], edges=[E("a", "t"), E("b", "m"), E("m", "p1"), E("m", "p2"), E("m", "p3"), E("m", "p4"), E("m", "p5")])

# Fig 4-20 (own version): confusion matrix, precision, recall, F-beta
D["ch04-precision-recall"] = dict(items=[
    T("Алерт есть", 330, -45, 20, "#495057"), T("Алерта нет", 690, -45, 20, "#495057"),
    T("Проблема\nбыла", 20, 30, 20, "#495057"), T("Проблемы\nне было", 20, 190, 20, "#495057"),
    N("tp", "TP: поймали\nнастоящую проблему", 250, 0, "g", 320, 120),
    N("fn", "FN: пропустили\nпроблему", 610, 0, "r", 320, 120),
    N("fp", "FP: ложная тревога", 250, 160, "r", 320, 120),
    N("tn", "TN: всё хорошо,\nтишина", 610, 160, "g", 320, 120),
    N("pr", "precision = TP / (TP + FP)\nиз всех алертов:\nсколько настоящих", 1050, 0, "p", 400, 120),
    N("rc", "recall = TP / (TP + FN)\nиз всех проблем:\nсколько поймали", 1050, 160, "p", 400, 120),
    N("fb", "F-beta: один балл из двух.\nbeta > 1: важнее recall.\nbeta < 1: важнее precision.", 1050, 320, "pu", 400, 130),
    N("w1", "Кричит «волк»:\nалерт на всё.\nrecall 100%,\nprecision низкая", 250, 340, "y", 320, 140),
    N("w2", "Спящий сторож:\nалертов нет.\nЛожных нет,\nно recall = 0", 610, 340, "y", 320, 140),
], edges=[])

# Figs 4-4..4-6, 4-21, 4-22 (own numbers): the threshold trade-off of the freshness detector
D["ch04-threshold-fscore"] = dict(items=[
    N("q", "SQL-запрос:\nдней с последнего\nобновления", 0, 0, "n", 280, 110),
    N("par", "Параметр T:\nпропуск больше T дней\nэто аномалия", 400, 0, "y", 320, 110),
    N("det", "Детектор\nшесть пропусков в\nданных, четыре настоящих", 840, 0, "pu", 340, 110),
    N("c1", "T = 1\nалерт на все 6 пропусков\nprecision 0,67\nrecall 1,00\nF1 0,80", 0, 290, "r", 300, 190),
    N("c3", "T = 3\nалерт на 4 пропуска\nprecision 0,75\nrecall 0,75\nF1 0,75", 360, 290, "y", 300, 190),
    N("c4", "T = 4\nалерт на 3 пропуска\nprecision 1,00\nrecall 0,75\nF1 0,86 (лучший)", 720, 290, "g", 300, 190),
    N("c7", "T = 7\nалерт на 2 пропуска\nprecision 1,00\nrecall 0,50\nF1 0,67", 1080, 290, "q", 300, 190),
    T("Низкий порог ловит всё, но шумит. Высокий порог молчит зря и пропускает проблемы.", 0, 520, 20, "#495057"),
    T("Данные: шесть пропусков, настоящие инциденты помечены вручную (ground truth).", 0, 560, 18),
], edges=[E("q", "par"), E("par", "det"), E("par", "c1"), E("par", "c3"), E("par", "c4"), E("par", "c7")])

# Fig 4-12 (own version): lineage helps find the root cause
D["ch04-lineage-root-cause"] = dict(items=[
    N("log", "schema_log\nснимки колонок\nпо дням", 0, 0, "db", 300, 110),
    N("pl", "planets\nисточник данных", 400, 0, "db", 300, 110),
    N("hb", "habitables\nпотребитель: считает\nhabitability", 800, 0, "db", 300, 110),
    N("i1", "5 августа в planets\nдобавили 2 колонки:\neccentricity, atmosphere", 400, 250, "y", 300, 130),
    N("i2", "5 августа в habitables\nдоля нулей в habitability\nвыросла с 0% до 50%", 800, 250, "r", 300, 130),
    N("mon", "Монитор схемы\nсравнивает снимок\nс предыдущим днём", 0, 250, "pu", 300, 130),
    N("x1", "Без lineage:\n«доля нулей выросла\nс 0% до 50%»\nНепонятно, почему", 0, 500, "n", 420, 140),
    N("x2", "С lineage:\n«5 августа в planets добавили колонки,\nэто сломало habitables, поэтому\nдоля нулей выросла»", 560, 500, "g", 540, 140),
], edges=[E("pl", "log", "снимок"), E("pl", "hb", "данные"), E("log", "mon", dashed=True),
          E("i1", "i2", "причина", dashed=True)])

if __name__ == "__main__":
    run_all(D)
