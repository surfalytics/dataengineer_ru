#!/usr/bin/env bash
# Chapter 6 ER diagrams: src/ch06-*.mmd -> public/assets/analytics-engineering-with-sql-and-dbt/*.png
# Usage: scripts/analytics-engineering-diagrams/ch06_mermaid.sh [name ...]   (no args = all ch06)
set -euo pipefail
cd "$(dirname "$0")/../.."
SRC=scripts/analytics-engineering-diagrams/src
OUT=public/assets/analytics-engineering-with-sql-and-dbt
CFG=scripts/kimball-diagrams/mermaid.json
mkdir -p "$OUT"
if [ $# -gt 0 ]; then FILES=(); for n in "$@"; do FILES+=("$SRC/$n.mmd"); done; else FILES=("$SRC"/ch06-*.mmd); fi
for f in "${FILES[@]}"; do
  n=$(basename "$f" .mmd)
  npx -y @mermaid-js/mermaid-cli -q -c "$CFG" -b white -s 2 -i "$f" -o "$OUT/$n.png"
  node -e "
const sharp=require('sharp');const p='$OUT/$n.png';
sharp(p).resize({width:1600,withoutEnlargement:true}).png({palette:true,quality:90,compressionLevel:9}).toBuffer().then(b=>require('fs').writeFileSync(p,b));"
  echo "ok $n $(wc -c < "$OUT/$n.png") bytes"
done
