#!/usr/bin/env python3
"""Считает слова прозы на странице: без front matter, блоков кода и <details>.
Запуск: python3 -I scripts/data-quality-fundamentals-code/wc_page.py <page.md>"""
import re
import sys

t = open(sys.argv[1], encoding="utf-8").read()
t = re.sub(r"\A---\n.*?\n---\n", "", t, flags=re.S)
t = re.sub(r"<details>.*?</details>", "", t, flags=re.S)
t = re.sub(r"```.*?```", "", t, flags=re.S)
t = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", t)
print(len(re.findall(r"[\w'’-]+", t)))
