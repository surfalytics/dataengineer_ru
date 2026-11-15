#!/usr/bin/env python3
"""Chapter 4 (when vibe coding isn't enough) diagrams. Usage: ch04_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

# Fig 4-1 (own version): tests force the split of one inline script into a testable core + thin DOM glue
D["ch04-testable-core"] = dict(items=[
    N("before", "До: один index.html\n\nразметка и стили\nсостояние строки\nобработка кликов\nчтение и запись\nlocalStorage\nобновление DOM", -300, 40, "r", 300, 330),
    Z("После: тестируемое ядро + тонкий слой", 180, -40, 1560, 640),
    N("html", "index.html\nоболочка страницы", 220, 40, "n", 260, 100),
    N("main", "main.js\nDOM glue: кнопка,\nсобытия, вывод", 700, 35, "y", 280, 110),
    N("texts", "texts.js\nстроки текста", 1200, 40, "n", 240, 100),
    N("core", "lineTrainer.js\nнавигация: next,\nпереход к началу", 220, 240, "g", 280, 110),
    N("store", "storage.js\nсохранить и\nзагрузить индекс", 700, 240, "g", 280, 110),
    N("ls", "localStorage\nбраузера", 1200, 245, "n", 240, 100),
    N("t1", "lineTrainer.test.js", 220, 440, "p", 280, 90),
    N("t2", "storage.test.js", 700, 440, "p", 280, 90),
    N("fake", "заглушка хранилища\n(в памяти)", 1200, 440, "p", 240, 90),
    T("Зелёное\nпроверяется\nбез браузера", 1500, 260, 18, "#2f9e44"),
], edges=[
    E("before", "html", "тесты\nтребуют"),
    E("html", "main", "подключает"),
    E("main", "texts"),
    E("main", "core"),
    E("main", "store"),
    E("store", "core", "импорт"),
    E("store", "ls", "в браузере", dashed=True),
    E("t1", "core", "Vitest"),
    E("t2", "store", "Vitest"),
    E("t2", "fake", "в тестах"),
])

# Table 4-1 (own version): layers of instructions and memory that enter one session
D["ch04-memory-layers"] = dict(items=[
    N("l1", "Поведение продукта\nмодель, инструменты, настройки", 0, 0, "n", 440, 80),
    N("l2", "Пользователь и организация\n~/.claude/CLAUDE.md, политики", 0, 100, "p", 440, 80),
    N("l3", "Проект\n./CLAUDE.md, .claude/rules/*.md", 0, 200, "p", 440, 80),
    N("l4", "Пути\nвложенные CLAUDE.md, rules с paths:", 0, 300, "p", 440, 80),
    N("l5", "auto memory\n~/.claude/projects/<project>/memory/", 0, 400, "pu", 440, 80),
    N("l6", "Текущая сессия\nчат, файлы, вывод команд", 0, 500, "y", 440, 80),
    N("l7", "Ваш prompt\nто, что вы только что ввели", 0, 600, "g", 440, 80),
    Z("Контекст запроса", 600, -60, 400, 760),
    N("s1", "как работает агент", 640, 10, "q", 320, 60),
    N("s2", "личные привычки", 640, 110, "q", 320, 60),
    N("s3", "команды, архитектура", 640, 210, "q", 320, 60),
    N("s4", "правила части дерева", 640, 310, "q", 320, 60),
    N("s5", "выученные заметки", 640, 410, "q", 320, 60),
    N("s6", "история разговора", 640, 510, "q", 320, 60),
    N("s7", "самый сильный сигнал", 640, 610, "q", 320, 60),
    T("синие пишете вы,\nфиолетовое пишет Claude", 1060, 60, 18, "#495057"),
    T("Это контекст, а не\nenforcement. Блокируют\nправа, hooks, sandbox\n(глава 5)", 1060, 470, 18, "#e03131"),
], edges=[E(f"l{i}", f"s{i}") for i in range(1, 8)])

# Own diagram instead of Fig 4-2 (screenshot of /context): context as a budget and two ways to compact
D["ch04-context-budget"] = dict(items=[
    N("c1", "System prompt", 0, 0, "n", 280, 60),
    N("c2", "Инструменты (tools)", 0, 80, "n", 280, 60),
    N("c3", "CLAUDE.md и память", 0, 160, "p", 280, 60),
    N("c4", "Skills", 0, 240, "n", 280, 60),
    N("c5", "Сообщения и\nвывод команд", 0, 320, "y", 280, 70),
    N("win", "Context window\n200K или 1M токенов\n\n/context: доли\nв токенах и %", 620, 0, "q", 300, 390),
    N("auto", "Автосжатие:\nв неудобный момент,\nдетали теряются", 1060, 20, "r", 300, 120),
    N("man", "/compact с целью:\nвы выбираете момент\nи что сохранить", 1060, 270, "g", 300, 120),
    N("chk", "Проверка: попросить\nсводку о проекте", 1500, 270, "g", 280, 120),
    N("file", "Важное заранее\nв CLAUDE.md", 620, 520, "p", 300, 90),
    T("Качество падает уже\nпосле 300–400K токенов", 1500, 50, 18, "#e03131"),
], edges=[
    E("c1", "win"), E("c2", "win"), E("c3", "win"), E("c4", "win"), E("c5", "win"),
    E("win", "auto", "окно\nполное"), E("win", "man", "лучше"),
    E("man", "chk"), E("file", "win", "читается\nв новой сессии", dashed=True),
])

if __name__ == "__main__":
    run_all(D)
