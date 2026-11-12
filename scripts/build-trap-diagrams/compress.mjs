// Shrink diagram PNGs: max 1600px wide, palette PNG.
// Run from the repo root: node scripts/build-trap-diagrams/compress.mjs [file ...]
import sharp from 'sharp';
import { readdirSync, readFileSync, writeFileSync } from 'node:fs';

const dir = 'public/assets/escaping-the-build-trap';
const files = process.argv.slice(2).length
  ? process.argv.slice(2)
  : readdirSync(dir).filter((f) => f.endsWith('.png')).map((f) => `${dir}/${f}`);

for (const file of files) {
  const input = readFileSync(file);
  const out = await sharp(input)
    .resize({ width: 1600, withoutEnlargement: true })
    .png({ palette: true, compressionLevel: 9 })
    .toBuffer();
  writeFileSync(file, out);
  console.log(file, `${Math.round(input.length / 1024)} KB -> ${Math.round(out.length / 1024)} KB`);
}
