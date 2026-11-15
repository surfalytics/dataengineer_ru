#!/usr/bin/env python3
"""Chapter 2 (AI evolution and tools) diagrams.
Usage: python3 scripts/redefining-de-ai-diagrams/ch02_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

# own (main): each tool of the chapter adds one ability to a bare LLM
D["ch02-ai-stack"] = dict(items=[
    T("Каждый шаг добавляет LLM одну новую способность", 0, -45, 22, "#495057"),
    N("llm", "LLM\n\nзнает только\nпубличные данные\nиз обучения", 0, 0, "n", 250, 170),
    N("pr", "+ prompt\n\nцель, контекст,\nисточник, формат\nответа", 310, 0, "p", 250, 170),
    N("rag", "+ RAG\n\nзнания компании:\nwiki, Slack,\nкаталоги, продажи", 620, 0, "db", 250, 170),
    N("mcp", "+ MCP\n\nдоступ к системам:\nбазы, API, файлы\nпо одному протоколу", 930, 0, "pu", 250, 170),
    N("ag", "+ агент\n\nплан, действия,\nпамять, проверка\nрезультата", 1240, 0, "g", 250, 170),
    T("отвечает", 70, 190, 18), T("отвечает точнее", 345, 190, 18),
    T("отвечает по своим\nданным", 650, 190, 18), T("читает и действует\nв системах", 960, 190, 18),
    T("сам доводит задачу\nдо конца", 1270, 190, 18),
], edges=[E("llm", "pr"), E("pr", "rag"), E("rag", "mcp"), E("mcp", "ag")])

# Figure 2-1 redrawn: RAG anatomy with the feedback loop
D["ch02-rag-anatomy"] = dict(items=[
    Z("Подготовка: заранее и по расписанию", -20, -60, 1000, 210),
    N("kb", "База знаний\n\nPDF, wiki, Jira,\nSlack, CSV, БД", 0, 0, "n", 260, 130),
    N("emb", "Chunking\nи embedding", 350, 15, "p", 260, 100),
    N("vdb", "Векторная база\n(индекс)", 700, 15, "db", 260, 100),
    N("q", "Вопрос\nпользователя", 0, 260, "y", 260, 100),
    N("srch", "Поиск по сходству:\ntop-k chunk", 700, 260, "p", 260, 100),
    N("llm", "LLM:\nsystem prompt +\nнайденный контекст\n+ вопрос", 1050, 245, "pu", 270, 130),
    N("ans", "Ответ\nпользователю", 1050, 470, "y", 270, 100),
    N("fb", "Обратная связь:\nлоги, оценки,\nисправления", 1420, 245, "q", 260, 130),
], edges=[E("kb", "emb"), E("emb", "vdb"), E("vdb", "srch"), E("q", "srch", "embedding вопроса"),
          E("srch", "llm"), E("llm", "ans"), E("ans", "fb"),
          E("fb", "vdb", "переиндексация", dashed=True), E("fb", "llm", dashed=True)])

# Figure 2-2 redrawn: MCP host, clients, servers and primitives
D["ch02-mcp-anatomy"] = dict(items=[
    N("user", "Пользователь", 0, 180, "y", 200, 90),
    Z("MCP host: Claude Code, IDE, чат", 250, -60, 600, 500),
    N("llm", "LLM\n\nрешает, какой\nинструмент\nвызвать", 290, 40, "n", 220, 360),
    N("c1", "MCP client 1", 590, 70, "p", 220, 100),
    N("c2", "MCP client 2", 590, 270, "p", 220, 100),
    N("s1", "MCP server\nбиблиотеки\n(каталог, продажи)", 960, 55, "pu", 280, 130),
    N("s2", "MCP server\nфайлов", 960, 270, "pu", 280, 100),
    N("t", "Tools: действия\nsearch_sales()", 1340, -40, "g", 290, 90),
    N("r", "Resources: данные\nдля чтения: схемы, логи", 1340, 80, "db", 290, 90),
    N("p", "Prompts: шаблоны\n«Найди {книгу} за 2025»", 1340, 200, "q", 290, 90),
], edges=[E("user", "llm"), E("llm", "c1"), E("llm", "c2"),
          E("c1", "s1", "JSON-RPC"), E("c2", "s2", "JSON-RPC"),
          E("s1", "t"), E("s1", "r"), E("s1", "p")])

# Figure 2-3 redrawn: agent anatomy with three exits of the feedback step
D["ch02-agent-anatomy"] = dict(items=[
    N("in", "Вход и контекст:\nцель, история,\nограничения", 0, 0, "n", 270, 110),
    N("plan", "Цель и план:\nподзадачи,\nпорядок, запасной путь", 390, 0, "p", 270, 110),
    N("rsn", "Рассуждение:\nкакой шаг\nсделать сейчас", 780, 0, "p", 270, 110),
    N("tool", "Инструменты\nи действия:\nCLI, API, SQL, RAG, MCP", 1170, 0, "pu", 280, 110),
    N("mem", "Память и состояние:\nчто сделано,\nчто упало", 1170, 300, "db", 280, 110),
    N("fb", "Обратная связь:\nцель достигнута?\nничего не сломано?", 780, 300, "q", 270, 110),
    N("out", "Вывод: статус,\nлоги, следующий шаг,\nвопрос человеку", 390, 300, "g", 270, 110),
    N("user", "Пользователь\nили система", 0, 300, "y", 270, 110),
    T("надо\nперепланировать", 640, 175, 18, "#495057"),
    T("ошибка:\nповтор", 945, 185, 18, "#495057"),
    T("готово", 680, 320, 18, "#495057"),
], edges=[E("in", "plan"), E("plan", "rsn"), E("rsn", "tool"), E("tool", "mem"), E("mem", "fb"),
          E("fb", "rsn", dashed=True), E("fb", "tool", dashed=True),
          E("fb", "out"), E("out", "user")])

if __name__ == "__main__":
    run_all(D)
