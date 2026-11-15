#!/usr/bin/env bash
# Git как кнопка «отменить»: чистый commit до задачи, просмотр diff, откат плохой правки.
# Запуск: bash scripts/claude-ai-bible-code/ch13_git_safety.sh (работает во временной папке).
set -euo pipefail
export GIT_AUTHOR_DATE="2026-01-01T10:00:00" GIT_COMMITTER_DATE="2026-01-01T10:00:00"
cd "$(mktemp -d)"
git init -q -b main
git config user.name "demo" && git config user.email "demo@example.com"
printf 'select order_id, amount_cents\nfrom orders\n' > orders.sql
git add -A && git commit -q -m "Чистое состояние до задачи"

echo "== 1. Перед задачей: рабочая копия чистая"
git status --short && echo "(нет изменений)"

echo "== 2. Агент поменял файл. Смотрим diff перед commit"
printf 'select order_id, amount_cents\nfrom orders\nwhere amount_cents > 0\n' > orders.sql
git diff --stat
git add -A && git commit -q -m "Фильтр пустых заказов"

echo "== 3. Следующая задача пошла не так: откатываем"
printf 'select *\nfrom orders\n' > orders.sql
echo "debug" > tmp_debug.txt
git status --short
git restore .            # отменяет правки в файлах под git
git clean -fdq           # удаляет новые файлы, которых нет в git
git status --short && echo "(снова чисто)"

echo "== 4. История: один commit на задачу"
git log --format='%s'
