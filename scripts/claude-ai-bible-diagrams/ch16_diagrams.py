#!/usr/bin/env python3
"""Chapter 16 (Model Context Protocol) diagrams. Usage: ch16_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

# own: tools x products before MCP, tools + products with MCP
D["ch16-n-times-m"] = dict(items=[
    Z("Раньше: своя связка на каждую пару", -25, -80, 820, 520),
    N("a1", "Claude Code", 0, 0, "p", 250, 90), N("a2", "Desktop", 0, 140, "p", 250, 90),
    N("a3", "Другой AI-ассистент", 0, 280, "p", 250, 90),
    N("t1", "База заказов", 520, 0, "db", 250, 90), N("t2", "Трекер задач", 520, 140, "db", 250, 90),
    N("t3", "Wiki", 520, 280, "db", 250, 90),
    T("3 × 3 = 9 самописных связок", 200, 390, 22, "#e03131"),
    Z("С MCP: каждое подключение один раз", 875, -80, 1000, 520),
    N("b1", "Claude Code", 900, 0, "p", 250, 90), N("b2", "Desktop", 900, 140, "p", 250, 90),
    N("b3", "Другой AI-ассистент", 900, 280, "p", 250, 90),
    N("mcp", "MCP\nобщий протокол", 1250, 125, "pu", 220, 120),
    N("s1", "MCP server:\nбаза заказов", 1580, 0, "g", 250, 90),
    N("s2", "MCP server:\nтрекер задач", 1580, 140, "g", 250, 90),
    N("s3", "MCP server:\nWiki", 1580, 280, "g", 250, 90),
    T("3 + 3 = 6 подключений", 1220, 390, 22, "#2f9e44"),
], edges=[E(a, t) for a in ("a1", "a2", "a3") for t in ("t1", "t2", "t3")]
  + [E(b, "mcp") for b in ("b1", "b2", "b3")] + [E("mcp", s) for s in ("s1", "s2", "s3")])

# own: host, clients, servers, external systems, three primitives (main diagram)
D["ch16-architecture"] = dict(items=[
    N("you", "Вы:\nзапрос", 0, 200, "n", 200, 100),
    Z("Host: Claude Code, Desktop, Cowork", 300, -80, 690, 620),
    N("model", "Claude\n(модель)", 340, 200, "y", 250, 100),
    N("c1", "Client 1", 700, 0, "p", 250, 100), N("c2", "Client 2", 700, 200, "p", 250, 100),
    N("c3", "Client 3", 700, 400, "p", 250, 100),
    N("s1", "Filesystem\nserver", 1120, 0, "g", 250, 100), N("s2", "Database\nserver", 1120, 200, "g", 250, 100),
    N("s3", "Chat server\n(удалённый)", 1120, 400, "g", 250, 100),
    Z("Внешние системы", 1460, -80, 330, 620),
    N("x1", "Папка проекта", 1500, 0, "n", 250, 100), N("x2", "База заказов", 1500, 200, "n", 250, 100),
    N("x3", "Командный чат", 1500, 400, "n", 250, 100),
    N("tl", "Tools: действия\n«отправь», «запусти»", 760, 640, "q", 280, 100),
    N("rs", "Resources: данные\nдля чтения", 1105, 640, "q", 280, 100),
    N("pr", "Prompts: готовые\nшаблоны задач", 1450, 640, "q", 280, 100),
    T("Что отдаёт каждый server:", 380, 670, 22, "#495057"),
], edges=[E("you", "model"), E("model", "c1"), E("model", "c2"), E("model", "c3"),
          E("c1", "s1", "stdio"), E("c2", "s2", "stdio"), E("c3", "s3", "HTTP"),
          E("s1", "x1"), E("s2", "x2"), E("s3", "x3"),
          E("s3", "tl", dashed=True), E("s3", "rs", dashed=True), E("s3", "pr", dashed=True)])

# own: confused deputy path with a human gate (the Melbourne case)
D["ch16-confused-deputy"] = dict(items=[
    N("web", "Веб-страница\nсо скрытой командой", 0, 0, "r", 240, 110),
    N("model", "Claude читает её\nи хочет отправить\nписьмо", 330, 0, "y", 240, 110),
    N("gate", "Человек\nподтверждает", 660, 0, "g", 240, 110),
    N("mail", "Email server\nс узким scope", 990, 0, "p", 240, 110),
    N("ok", "Письмо\nколлегам", 1320, 0, "g", 240, 110),
    N("no", "Письмо незнакомцу\nне уходит", 660, 260, "r", 240, 110),
    Z("Слои защиты", -25, 440, 1610, 200),
    N("d1", "Вывод tools —\nнедоверенный ввод", 0, 500, "n", 360, 100),
    N("d2", "Least privilege:\nминимум прав", 400, 500, "n", 360, 100),
    N("d3", "Секреты в env,\nротация ключей", 800, 500, "n", 360, 100),
    N("d4", "Серверы только\nиз надёжных источников", 1200, 500, "n", 360, 100),
], edges=[E("web", "model"), E("model", "gate"), E("gate", "mail"), E("mail", "ok"),
          E("gate", "no", "подозрительно", dashed=True)])

if __name__ == "__main__":
    run_all(D)
