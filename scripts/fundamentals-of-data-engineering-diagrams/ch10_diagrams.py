#!/usr/bin/env python3
"""Chapter 10 (security and privacy) diagrams. Usage: ch10_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

# main: people, processes, technology, and the main risk of each
D["ch10-security-layers"] = dict(items=[
    N("p", "Люди", 0, 0, "r", 300, 90),
    N("pr", "Процессы", 460, 0, "y", 300, 90),
    N("t", "Технологии", 920, 0, "p", 300, 90),
    N("p2", "Паранойя с credentials,\nменьше данных, этика", 0, 170, "n", 300, 110),
    N("pr2", "Привычка вместо театра,\nleast privilege, backup", 460, 170, "n", 300, 110),
    N("t2", "Patch, шифрование,\nмониторинг, сеть", 920, 170, "n", 300, 110),
    N("p3", "Риск: человек —\nслабое звено", 0, 370, "r", 300, 100),
    N("pr3", "Риск: shared responsibility,\nошибки настройки у вас", 460, 370, "r", 300, 100),
    N("t3", "Риск: шифрование\nне заменяет контроль доступа", 920, 370, "r", 300, 100),
], edges=[E("p", "pr", "потом"), E("pr", "t", "потом"),
          E("p", "p2"), E("pr", "pr2"), E("t", "t2"),
          E("p2", "p3"), E("pr2", "pr3"), E("t2", "t3")])

# least privilege: normal access vs broken glass
D["ch10-least-privilege"] = dict(items=[
    Z("Обычный доступ: least privilege", -20, -60, 1380, 220),
    N("a1", "Появилась задача", 0, 0, "p", 260, 100),
    N("a2", "Выдаём только нужные\nIAM roles на срок задачи", 360, 0, "g", 260, 100),
    N("a3", "Работа через views,\nмаскированный PII,\nправа на колонки и строки", 720, 0, "g", 260, 100),
    N("a4", "Задача закончена:\nроли отозваны", 1080, 0, "n", 260, 100),
    Z("Редкие данные: broken glass", -20, 250, 1380, 220),
    N("b1", "Авария или срочный\nзапрос истории", 0, 310, "q", 260, 100),
    N("b2", "Экстренное\nсогласование", 360, 310, "y", 260, 100),
    N("b3", "Доступ к данным,\nкоторые хранят,\nно почти не читают", 720, 310, "r", 260, 100),
    N("b4", "Работа сделана:\nдоступ закрыт сразу", 1080, 310, "n", 260, 100),
], edges=[E("a1", "a2"), E("a2", "a3"), E("a3", "a4"),
          E("b1", "b2"), E("b2", "b3"), E("b3", "b4")])

# encryption: where it is applied and what it does not cover
D["ch10-encryption"] = dict(items=[
    N("cl", "Клиент или ноутбук\n(full-disk encryption)", 0, 0, "p", 260, 100),
    N("api", "Облачный API\nили сервис", 480, 0, "g", 240, 100),
    N("st", "Базы, файловые системы,\nobject storage, backups", 940, 0, "db", 280, 100),
    N("no", "Шифрование не поможет: украдены credentials, bucket открыт всем,\nключи хранят плохо. Для этого нужны least privilege и контроль сети.", 0, 230, "r", 1220, 100),
], edges=[E("cl", "api", "HTTPS, не FTP"), E("api", "st", "server-side\nencryption")])

# monitoring: four areas -> one dashboard -> alerts and incident plan
D["ch10-monitoring"] = dict(items=[
    N("m1", "Access\nкто, что, когда, откуда", 0, 0, "p", 300, 100),
    N("m2", "Resources\nCPU, память, диск, I/O", 340, 0, "db", 300, 100),
    N("m3", "Billing\nрезкий рост счёта", 680, 0, "q", 300, 100),
    N("m4", "Excess permissions\nнеиспользуемые права", 1020, 0, "pu", 300, 100),
    N("d", "Общий dashboard для всей команды данных", 330, 240, "g", 660, 90),
    N("al", "Alerts и поиск аномалий", 330, 430, "y", 300, 90),
    N("ir", "План реакции на инциденты:\nрепетируют регулярно", 690, 430, "r", 300, 90),
], edges=[E("m1", "d"), E("m2", "d"), E("m3", "d"), E("m4", "d"),
          E("d", "al"), E("d", "ir")])

if __name__ == "__main__":
    run_all(D)
