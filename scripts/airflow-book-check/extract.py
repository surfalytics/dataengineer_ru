#!/usr/bin/env python3
"""Write every ```python block of the Airflow book pages to <out>/chNN_<i>.py."""
import glob, os, re, sys

PAGES = "src/content/docs/book-summaries/engineering/data-pipelines-with-apache-airflow"
out = sys.argv[1]
os.makedirs(out, exist_ok=True)
for f in sorted(glob.glob(f"{PAGES}/[01]*.md")):
    text = open(f, encoding="utf-8").read()
    for i, block in enumerate(re.findall(r"```python\n(.*?)```", text, re.S)):
        open(f"{out}/ch{os.path.basename(f)[:2]}_{i}.py", "w", encoding="utf-8").write(block)
