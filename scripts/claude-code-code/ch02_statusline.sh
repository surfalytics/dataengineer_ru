#!/usr/bin/env bash
# Простая statusline для Claude Code: папка | модель | ветка и состояние git.
# Claude Code передаёт данные о сессии в stdin как JSON. Нужен jq.
input=$(cat)
dir=$(echo "$input" | jq -r '.workspace.current_dir')
model=$(echo "$input" | jq -r '.model.display_name')
branch=$(git -C "$dir" branch --show-current 2>/dev/null)
if [ -n "$branch" ]; then
  # пустой вывод git status --porcelain значит «нет изменений»
  if [ -z "$(git -C "$dir" status --porcelain 2>/dev/null)" ]; then state="clean"; else state="dirty"; fi
  echo "📁 $(basename "$dir") | 🤖 $model | 🌿 $branch ($state)"
else
  echo "📁 $(basename "$dir") | 🤖 $model"
fi
