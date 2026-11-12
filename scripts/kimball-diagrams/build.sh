#!/usr/bin/env bash
# Render every scripts/kimball-diagrams/src/*.mmd to public/assets/data-warehouse-toolkit/*.png
# Usage: scripts/kimball-diagrams/build.sh [name ...]   (no args = all)
set -euo pipefail
cd "$(dirname "$0")/../.."
SRC=scripts/kimball-diagrams/src
OUT=public/assets/data-warehouse-toolkit
mkdir -p "$OUT"
CFG=scripts/kimball-diagrams/mermaid.json
if [ $# -gt 0 ]; then FILES=(); for n in "$@"; do FILES+=("$SRC/$n.mmd"); done; else FILES=("$SRC"/*.mmd); fi
for f in "${FILES[@]}"; do
  n=$(basename "$f" .mmd)
  npx -y @mermaid-js/mermaid-cli -q -c "$CFG" -b white -s 2 -i "$f" -o "$OUT/$n.png"
  # compress: PNG palette, max 1600px wide
  node -e "
const sharp=require('sharp');const p='$OUT/$n.png';
sharp(p).resize({width:1600,withoutEnlargement:true}).png({palette:true,quality:90,compressionLevel:9}).toBuffer().then(b=>require('fs').writeFileSync(p,b));"
  echo "ok $n $(wc -c < "$OUT/$n.png") bytes"
done
