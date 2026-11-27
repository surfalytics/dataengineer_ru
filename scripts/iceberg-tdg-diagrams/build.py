#!/usr/bin/env python3
"""Render saved Excalidraw scenes: python3 build.py [--cli PATH] [SCENE ...]."""
import argparse
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / 'public/assets/apache-iceberg-the-definitive-guide'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--cli', default='excalidraw-canvas', help='Excalidraw CLI executable (default: search PATH)')
parser.add_argument('scenes', nargs='*', help='scene names without extension; default: all scenes')
args = parser.parse_args()
scenes = [HERE / 'src' / (Path(name).stem + '.excalidraw') for name in args.scenes] if args.scenes else sorted((HERE / 'src').glob('*.excalidraw'))
OUT.mkdir(parents=True, exist_ok=True)
for scene in scenes:
    if not scene.is_file():
        parser.error(f'scene not found: {scene}')
    target = OUT / (scene.stem + '.png')
    subprocess.run([args.cli, 'render', str(scene), '--out', str(target), '--scale', '2', '--padding', '30'], check=True)
    subprocess.run(['node', '-e', "const s=require('sharp'),fs=require('fs');const p=process.argv[1];s(p).resize({width:1600,withoutEnlargement:true}).png({palette:true,compressionLevel:9}).toBuffer().then(b=>fs.writeFileSync(p,b)).catch(e=>{console.error(e);process.exit(1)})", str(target)], cwd=ROOT, check=True)
    if target.stat().st_size >= 200_000:
        raise SystemExit(f'{target}: exceeds 200 KB')
    print(f'{scene.name}: {target.stat().st_size} bytes')
