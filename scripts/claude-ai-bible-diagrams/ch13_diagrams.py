#!/usr/bin/env python3
"""Chapter 13 (Claude Code) diagrams. Usage: ch13_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

# own (book text, no figure): explore, plan, edit, run, iterate (main diagram)
D["ch13-agent-loop"] = dict(items=[
    N("you", "Вы описываете\nнужный результат", -40, 0, "y"),
    N("exp", "1. Explore:\nчитает файлы,\nищет связи", 320, 0, "db"),
    N("plan", "2. Plan:\nкакие файлы\nи в каком порядке", 640, 0, "p"),
    N("ok", "План\nвам подходит?", 1000, -20, "y", 250, 140, "diamond"),
    N("fix", "Вы правите план:\n«этот файл\nне трогать»", 1000, -280, "y"),
    N("edit", "3. Edit:\nправки,\ndiff по файлам", 1000, 260, "pu"),
    N("run", "4. Run:\nтесты, linter,\nсборка", 640, 260, "p"),
    N("chk", "Тесты\nпрошли?", 320, 240, "q", 230, 140, "diamond"),
    N("done", "Готово: отчёт.\nВы читаете diff\nи делаете commit", -40, 260, "g"),
    N("iter", "5. Iterate:\nищет причину\nи чинит", 640, 520, "r"),
], edges=[E("you", "exp"), E("exp", "plan"), E("plan", "ok"),
          E("ok", "fix", "нет"), E("fix", "plan"), E("ok", "edit", "да"),
          E("edit", "run"), E("run", "chk"), E("chk", "done", "да"),
          E("chk", "iter", "нет"), E("iter", "edit")])

# own: main agent hands focused tasks to subagents, gets summaries back
D["ch13-subagents"] = dict(items=[
    N("you", "Вы: задача из трёх\nнезависимых частей", 480, -260, "y", 300, 100),
    N("main", "Главный агент:\nдержит общий план,\nраздаёт части", 480, 0, "p", 300, 110),
    N("s1", "Subagent 1:\nтесты модуля цен\n(свой контекст)", 40, 280, "pu", 300, 110),
    N("s2", "Subagent 2:\nтесты скидок\n(свой контекст)", 480, 280, "pu", 300, 110),
    N("s3", "Subagent 3:\nфункции длиннее\n80 строк", 920, 280, "pu", 300, 110),
    N("res", "Главный агент собирает\nкороткие сводки\nи отчитывается вам", 480, 580, "g", 300, 110),
    T("Каждый subagent читает много файлов.\nВ главный контекст попадает только вывод.", 900, 600, 18),
], edges=[E("you", "main"), E("main", "s1", "задача"), E("main", "s2", "задача"),
          E("main", "s3", "задача"), E("s1", "res", "сводка"), E("s2", "res", "сводка"),
          E("s3", "res", "сводка")])

# own: where hooks fire in the session
D["ch13-hooks"] = dict(items=[
    N("start", "SessionStart:\nсессия началась", 0, 0, "n"),
    N("want", "Агент хочет\nзапустить\nинструмент", 330, 0, "p"),
    N("pre", "PreToolUse:\nhook проверяет\nкоманду", 660, 0, "q"),
    N("tool", "Инструмент\nработает:\nEdit, Bash", 1090, 0, "p"),
    N("blk", "exit 2: команда\nзаблокирована,\nагент видит причину", 660, -260, "r"),
    N("post", "PostToolUse:\nformat\nи typecheck", 1090, 260, "q"),
    N("stop", "Stop: агент\nсчитает, что\nзакончил", 1560, 260, "n"),
], edges=[E("start", "want"), E("want", "pre"), E("pre", "tool", "разрешено"),
          E("pre", "blk", "запрет"), E("tool", "post"), E("post", "stop", "задача сделана"),
          E("post", "want", "следующий шаг", dashed=True)])

# own: git as the undo button
D["ch13-git-safety"] = dict(items=[
    N("st", "1. git status:\nрабочая копия\nчистая", 0, 0, "n"),
    N("task", "2. Задача\nдля Claude Code", 330, 0, "p"),
    N("diff", "3. git diff:\nчитаете все правки\nсвежим взглядом", 660, 0, "y"),
    N("ok", "Правки\nхорошие?", 990, -20, "q", 250, 140, "diamond"),
    N("commit", "4. git commit:\nодин commit\nна задачу", 990, 280, "g"),
    N("back", "git restore .\nили git reset --hard:\nназад к commit", 975, -320, "r", 280, 100),
], edges=[E("st", "task"), E("task", "diff"), E("diff", "ok"),
          E("ok", "commit", "да"), E("ok", "back", "нет"),
          E("commit", "st", "следующая задача", dashed=True),
          E("back", "task", "заново, с планом", dashed=True)])

if __name__ == "__main__":
    run_all(D)
