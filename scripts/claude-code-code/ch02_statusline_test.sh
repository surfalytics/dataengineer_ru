#!/usr/bin/env bash
# Проверка statusline без Claude Code: свой git-репозиторий во временной папке и JSON как от Claude Code.
set -e
here=$(cd "$(dirname "$0")" && pwd)
tmp=$(mktemp -d)
mkdir "$tmp/lyrics-trainer" && cd "$tmp/lyrics-trainer"
git init -q -b main && git -c user.name=t -c user.email=t@t commit -q --allow-empty -m init
json='{"model":{"display_name":"Opus"},"workspace":{"current_dir":"'"$tmp/lyrics-trainer"'"}}'
echo "$json" | bash "$here/ch02_statusline.sh"
touch index.html
echo "$json" | bash "$here/ch02_statusline.sh"
rm -rf "$tmp"
