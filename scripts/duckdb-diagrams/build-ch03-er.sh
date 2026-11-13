#!/usr/bin/env bash
# Render the chapter 3 ER diagram (Mermaid) to public/assets/duckdb-up-and-running/ch03-shop-er.png
set -euo pipefail
cd "$(dirname "$0")/../.."
OUT=public/assets/duckdb-up-and-running/ch03-shop-er.png
npx -y @mermaid-js/mermaid-cli -q -c scripts/kimball-diagrams/mermaid.json -b white -s 2 -i scripts/duckdb-diagrams/src/ch03-shop-er.mmd -o "$OUT"
node -e "
const sharp=require('sharp');const p='$OUT';
sharp(p).resize({width:1600,withoutEnlargement:true}).png({palette:true,quality:90,compressionLevel:9}).toBuffer().then(b=>require('fs').writeFileSync(p,b));"
echo "ok $(wc -c < "$OUT") bytes"
