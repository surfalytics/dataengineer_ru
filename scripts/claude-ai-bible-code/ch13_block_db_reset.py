#!/usr/bin/env python3
"""PreToolUse hook для Claude Code: не даёт агенту сбросить базу вне локальной среды.

Claude Code передаёт в stdin JSON с полями tool_name и tool_input.
Код выхода 2 блокирует команду, текст из stderr получает агент.
Подключение: .claude/settings.json, событие PreToolUse, matcher "Bash".
"""
import json
import os
import sys

DANGEROUS = ("db:reset", "migrate:fresh", "dropdb", "--full-refresh")


def main() -> int:
    event = json.load(sys.stdin)
    if event.get("tool_name") != "Bash":
        return 0
    command = event.get("tool_input", {}).get("command", "")
    hit = [word for word in DANGEROUS if word in command]
    if hit and os.environ.get("APP_ENV") != "local":
        print(f"Заблокировано: '{hit[0]}' разрешён только при APP_ENV=local", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
