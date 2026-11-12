#!/usr/bin/env python3
"""Build all Airflow book diagrams. Specs live in specs/chNN.py and fill D.
Usage: excalidraw_build.py [name ...]   (no args = all)"""
import importlib, pkgutil, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import lib, specs
D = {}
for m in pkgutil.iter_modules(specs.__path__):
    D.update(importlib.import_module("specs." + m.name).D)
if __name__ == "__main__":
    names = sys.argv[1:] or list(D)
    lib.OUT.mkdir(parents=True, exist_ok=True)
    for n in names:
        lib.run(n, D[n])
