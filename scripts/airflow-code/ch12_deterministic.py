"""Глава 12: источник недетерминизма (порядок set) и лекарство (sorted, seed).
Hash seed фиксируем в дочернем процессе, чтобы вывод был одинаковым при каждом запуске.
Запуск: python3 -I ch12_deterministic.py"""
import os
import subprocess
import sys

CHILD = (
    "words = {'orders', 'users', 'events', 'clicks', 'refunds'}\n"
    "print('без sort:', list(words))\n"
    "print('с sorted:', sorted(words))\n"
)

for seed in ("1", "2"):
    env = {**os.environ, "PYTHONHASHSEED": seed}
    out = subprocess.run([sys.executable, "-c", CHILD], env=env, capture_output=True, text=True, check=True).stdout
    print(f"PYTHONHASHSEED={seed}")
    print(out.rstrip())

import random  # noqa: E402

print("random с фиксированным seed даёт одни и те же числа:")
for _ in range(2):
    rnd = random.Random(42)
    print("  seed=42:", [rnd.randint(1, 100) for _ in range(3)])
