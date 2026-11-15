#!/usr/bin/env python3
"""Проверка hook ch13_block_db_reset.py: подаём ему такие же JSON, как Claude Code."""
import json
import os
import subprocess
import sys
from pathlib import Path

HOOK = Path(__file__).with_name("ch13_block_db_reset.py")

CASES = [  # команда агента, значение APP_ENV
    ("npm test", None),
    ("npm run db:reset", None),
    ("npm run db:reset", "local"),
    ("dbt run --full-refresh --target prod", "prod"),
]

for command, app_env in CASES:
    env = {k: v for k, v in os.environ.items() if k != "APP_ENV"}
    if app_env:
        env["APP_ENV"] = app_env
    event = {"hook_event_name": "PreToolUse", "tool_name": "Bash",
             "tool_input": {"command": command}}
    r = subprocess.run([sys.executable, "-I", str(HOOK)], input=json.dumps(event),
                       capture_output=True, text=True, env=env)
    verdict = "пропущено" if r.returncode == 0 else "блок"
    print(f"{command:<38} APP_ENV={app_env or '-':<6} exit={r.returncode} {verdict} {r.stderr.strip()}".rstrip())
