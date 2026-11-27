import { execFileSync } from 'node:child_process';
import {
  mkdirSync, mkdtempSync, readdirSync, readFileSync,
  realpathSync, renameSync, rmSync, writeFileSync,
} from 'node:fs';
import { basename, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import sharp from 'sharp';

const sources = fileURLToPath(new URL('./src/', import.meta.url));
const output = fileURLToPath(new URL('../../public/assets/practical-lakehouse-architecture/', import.meta.url));
const defaultCli = new URL('../../../excalidraw-canvas/node_modules/.bin/excalidraw-canvas', import.meta.url);
const cli = realpathSync(process.env.EXCALIDRAW_CLI || fileURLToPath(defaultCli));
const { embedPngScene } = await import(new URL('./core/png-scene.js', pathToFileURL(cli)));
const scenes = readdirSync(sources).filter(name => name.endsWith('.excalidraw')).sort();

if (scenes.length === 0) throw new Error('Нет сцен Excalidraw для экспорта');

mkdirSync(output, { recursive: true });
const temporary = mkdtempSync(join(output, '.excalidraw-'));
const images = [];
try {
  for (const scene of scenes) {
    const name = basename(scene, '.excalidraw');
    const source = join(sources, scene);
    const raw = join(temporary, `${name}-raw.png`);
    const image = `${name}.png`;
    execFileSync(process.execPath, [cli, 'render', source, '--out', raw, '--scale', '2', '--padding', '22'], {
      stdio: ['ignore', 'ignore', 'pipe'],
    });
    const compressed = await sharp(raw)
      .resize({ width: 1500, withoutEnlargement: true })
      .png({ palette: true, colours: 96 })
      .toBuffer();
    const sceneJson = JSON.stringify(JSON.parse(readFileSync(source, 'utf8')));
    const editable = embedPngScene(compressed, sceneJson);
    if (editable.length >= 200_000) throw new Error(`${image} превышает лимит в 200 КБ`);
    writeFileSync(join(temporary, image), editable);
    images.push(image);
  }

  for (const image of images) {
    renameSync(join(temporary, image), join(output, image));
  }
  console.log(`Экспортировано схем: ${images.length}`);
} finally {
  rmSync(temporary, { recursive: true, force: true });
}
