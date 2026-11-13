#!/usr/bin/env python3
"""Считает слова главы книги из текстового файла: без колонтитулов и подписей рисунков.
Код книги нужно вычесть вручную (оцените по числу строк кода).
Запуск: python3 -I wc_book.py <chNN.txt>"""
import re
import sys

n = 0
for line in open(sys.argv[1], encoding="utf-8"):
    s = line.strip()
    if not s or re.fullmatch(r"\d+", s) or re.search(r"\|\s+(Chapter \d+|Preface)|(Chapter \d+|Preface)\s+\|", s):
        continue
    if re.match(r"Figure \d+-\d+\.", s):
        continue
    n += len(re.findall(r"[\w'’-]+", s))
print(n)
