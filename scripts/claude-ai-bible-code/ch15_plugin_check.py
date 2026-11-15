#!/usr/bin/env python3
"""Глава 15: собрать plugin release-notes-kit во временной папке, проверить manifest
и проверить, честно ли поднята версия. Только стандартная библиотека.
Запуск: python3 -I scripts/claude-ai-bible-code/ch15_plugin_check.py"""
import json
import tempfile
from pathlib import Path

# Части plugin: путь -> содержимое. Claude Code находит их по стандартным папкам.
FILES = {
    "skills/format-release-notes/SKILL.md":
        "---\nname: format-release-notes\n"
        "description: Пишет заметки о релизе по задачам из трекера.\n---\n",
    "commands/release-notes.md": "Собери заметки о релизе за текущий цикл.\n",
    "agents/style-checker.md": "Сверь заметки с правилами стиля команды.\n",
    ".mcp.json": json.dumps({"mcpServers": {"tracker": {"command": "tracker-mcp"}}}),
}

MANIFEST = {
    "name": "release-notes-kit",
    "version": "1.2.0",
    "description": "Пишет и проверяет заметки о релизе по задачам из трекера. "
                   "Используй, чтобы написать release notes или changelog.",
    "author": {"name": "Platform Team"},
}


def build(root: Path) -> None:
    """Раскладывает файлы plugin по папкам."""
    for rel, text in FILES.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    m = root / ".claude-plugin" / "plugin.json"
    m.parent.mkdir(parents=True, exist_ok=True)
    m.write_text(json.dumps(MANIFEST, ensure_ascii=False, indent=2), encoding="utf-8")


def check_manifest(root: Path) -> list[str]:
    """Простые проверки: manifest читается, поля на месте, версия вида X.Y.Z."""
    m = json.loads((root / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    problems = [f"нет поля {k}" for k in ("name", "version", "description") if k not in m]
    parts = m.get("version", "").split(".")
    if len(parts) != 3 or not all(x.isdigit() for x in parts):
        problems.append("версия не в формате X.Y.Z")
    if len(m.get("description", "")) < 40:
        problems.append("описание слишком короткое: по нему люди и Claude понимают plugin")
    return problems


def needed_bump(old: dict, new: dict) -> str:
    """Какой номер версии надо поднять. Убрали то, чем люди пользуются, -> major."""
    removed = sorted(set(old["commands"]) - set(new["commands"]))
    added = sorted(set(new["commands"]) - set(old["commands"]))
    if removed or old["output"] != new["output"]:
        return "major"
    return "minor" if added else "patch"


def actual_bump(old_v: str, new_v: str) -> str:
    a, b = [list(map(int, v.split("."))) for v in (old_v, new_v)]
    return "major" if b[0] > a[0] else "minor" if b[1] > a[1] else "patch"


def check_release(old: dict, new: dict) -> str:
    need, got = needed_bump(old, new), actual_bump(old["version"], new["version"])
    order = ["patch", "minor", "major"]
    verdict = "ok" if order.index(got) >= order.index(need) else f"ОШИБКА: нужен {need}"
    return f'{old["version"]} -> {new["version"]}: поднят {got}, нужен {need}. {verdict}'


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "release-notes-kit"
        build(root)
        print("Файлы plugin:")
        for p in sorted(root.rglob("*")):
            if p.is_file():
                print("  " + p.relative_to(root).as_posix())
        problems = check_manifest(root)
        print("Проверка manifest:", "ok" if not problems else "; ".join(problems))

    v12 = {"version": "1.2.0", "commands": ["release-notes"], "output": "markdown"}
    v13 = {"version": "1.3.0", "commands": ["release-notes", "changelog"], "output": "markdown"}
    v14 = {"version": "1.4.0", "commands": ["notes", "changelog"], "output": "markdown"}
    v20 = {"version": "2.0.0", "commands": ["notes", "changelog"], "output": "markdown"}
    print("Проверка версий:")
    print("  " + check_release(v12, v13))  # новая команда: хватит minor
    print("  " + check_release(v13, v14))  # переименовали команду, но подняли только minor
    print("  " + check_release(v13, v20))  # то же переименование, честный major
