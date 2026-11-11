"""Рисует графики для уроков курса «Базовый минимум статистики».

Результат: public/assets/practice/stats/*.svg
Запуск из корня репозитория: python3 scripts/stats-practice/charts.py
Данные берутся из учебных файлов (сначала запустите build.py). Нужен только python3.
"""

import csv
import io
import math
import random
import statistics as st
import tarfile
from pathlib import Path

OUT = Path("public/assets/practice/stats")
OUT.mkdir(parents=True, exist_ok=True)
tar = tarfile.open("public/assets/practice/stats-practice.tar.gz")


def table(name):
    return list(csv.DictReader(io.TextIOWrapper(tar.extractfile(f"stats-practice/data/{name}"), encoding="utf-8")))


BLUE, BLUE_D, RED, GREEN, GRAY, INK = "#a5d8ff", "#1971c2", "#e03131", "#2f9e44", "#495057", "#1e1e1e"
LINE = "#adb5bd"  # оси и рамки
FONT = "font-family=\"system-ui, -apple-system, 'Segoe UI', sans-serif\""


def svg(w, h, title, body):
    # Белая карточка с рамкой: график одинаково читается в светлой и тёмной теме сайта.
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{title}">'
        f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="14" fill="#ffffff" stroke="#dee2e6" stroke-width="2"/>{body}</svg>'
    )


def text(x, y, s, size=18, color=INK, anchor="start", weight="normal", rotate=None):
    tr = f' transform="rotate({rotate} {x} {y})"' if rotate else ""
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}" {FONT}{tr}>{s}</text>'


def save(name, w, h, title, body):
    (OUT / name).write_text(svg(w, h, title, body), encoding="utf-8")
    print(name)


# 1. Среднее и медиана ---------------------------------------------------------
amount = [float(r["amount"]) for r in table("orders.csv")]
mean, med = st.mean(amount), st.median(amount)
bins = [0] * 20  # 0-20, 20-40, ... 380-400
big = 0
for a in amount:
    if a < 400:
        bins[int(a // 20)] += 1
    else:
        big += 1
W, H = 960, 520
x0, base, bw, top = 100, 410, 40, 140
scale = (base - top) / max(bins)
b = text(W / 2, 42, "Суммы заказов: большие заказы тянут среднее вправо", 24, anchor="middle", weight="bold")
for frac in (0, 0.5, 1):  # линии сетки и подписи оси «число заказов»
    n = round(max(bins) * frac)
    y = base - n * scale
    b += f'<line x1="{x0}" y1="{y}" x2="{x0 + 20 * bw}" y2="{y}" stroke="#e9ecef" stroke-width="1"/>'
    b += text(x0 - 12, y + 6, str(n), 16, GRAY, "end")
b += text(x0, top - 62, "число заказов", 16, GRAY, "start")
for i, n in enumerate(bins):
    hgt = n * scale
    b += f'<rect x="{x0 + i * bw + 1}" y="{base - hgt}" width="{bw - 2}" height="{hgt}" fill="{BLUE}" stroke="{BLUE_D}" stroke-width="1.5"/>'
b += f'<line x1="{x0}" y1="{base}" x2="{x0 + 20 * bw}" y2="{base}" stroke="{INK}" stroke-width="2"/>'
for v in (0, 100, 200, 300, 400):
    b += f'<line x1="{x0 + v / 20 * bw}" y1="{base}" x2="{x0 + v / 20 * bw}" y2="{base + 6}" stroke="{INK}" stroke-width="2"/>'
    b += text(x0 + v / 20 * bw, base + 30, str(v), 18, GRAY, "middle")
b += text(x0 + 10 * bw, base + 64, "сумма заказа", 18, GRAY, "middle")
for val, label, col in ((med, f"медиана {med:.0f}", GREEN), (mean, f"среднее {mean:.0f}", RED)):
    x = x0 + val / 20 * bw
    b += f'<line x1="{x}" y1="{top - 36}" x2="{x}" y2="{base}" stroke="{col}" stroke-width="4" stroke-dasharray="9 6"/>'
    b += text(x + (-10 if col == GREEN else 10), top - 24, label, 20, col, "end" if col == GREEN else "start", "bold")
b += text(x0 + 20 * bw, 215, f"ещё {big} заказов дороже 400", 18, RED, "end")
b += text(x0 + 20 * bw, 240, "(до 4 493) за пределами графика →", 18, RED, "end")
save("mean-vs-median.svg", W, H, "Гистограмма сумм заказов. Среднее правее медианы", b)

# 2. Нормальное распределение -------------------------------------------------
d = [float(r["delivery_hours"]) for r in table("orders.csv")]
m, s = st.mean(d), st.stdev(d)
W, H, bx, by, sx = 960, 480, 50, 340, 105  # sx — пикселей на одно s
pdf = lambda z: math.exp(-z * z / 2) / math.sqrt(2 * math.pi)
yy = lambda z: by - pdf(z) * 720
b = text(W / 2, 42, "Нормальное распределение: время доставки (часы)", 24, anchor="middle", weight="bold")
cx = W / 2
for k, col in ((3, "#e7f5ff"), (2, "#d0ebff"), (1, BLUE)):
    pts = [(-k + i * 2 * k / 60) for i in range(61)]
    poly = " ".join(f"{cx + z * sx:.1f},{yy(z):.1f}" for z in pts)
    b += f'<polygon points="{cx - k * sx},{by} {poly} {cx + k * sx},{by}" fill="{col}"/>'
curve = " ".join(f"{cx + z * sx:.1f},{yy(z):.1f}" for z in [(-3.5 + i * 7 / 100) for i in range(101)])
b += f'<polyline points="{curve}" fill="none" stroke="{BLUE_D}" stroke-width="4"/>'
b += f'<line x1="{bx}" y1="{by}" x2="{W - bx}" y2="{by}" stroke="{INK}" stroke-width="2"/>'
for k in range(-3, 4):
    b += f'<line x1="{cx + k * sx}" y1="{by}" x2="{cx + k * sx}" y2="{by + 8}" stroke="{INK}" stroke-width="2"/>'
    lab = "μ" if k == 0 else (f"μ{k:+d}σ".replace("+1σ", "+σ").replace("-1σ", "−σ").replace("-", "−"))
    b += text(cx + k * sx, by + 34, lab, 20, INK, "middle")
    b += text(cx + k * sx, by + 60, f"{m + k * s:.0f} ч", 18, GRAY, "middle")
b += text(cx, 215, "68%", 28, BLUE_D, "middle", "bold")
b += text(cx - 1.5 * sx, 314, "95%", 20, BLUE_D, "middle", "bold")
b += text(cx + 1.5 * sx, 314, "95%", 20, BLUE_D, "middle", "bold")
b += text(W / 2, 440, f"μ — среднее ({m:.1f} ч), σ — стандартное отклонение ({s:.1f} ч)", 18, GRAY, "middle")
b += text(W / 2, 466, "68% данных в пределах ±1σ, 95% в пределах ±2σ, 99,7% в пределах ±3σ", 18, GRAY, "middle")
save("normal-distribution.svg", W, H, "Нормальное распределение: 68, 95 и 99,7 процентов данных", b)

# 3. Boxplot --------------------------------------------------------------------
q1, q2, q3 = st.quantiles(amount, n=4, method="inclusive")
fence = q3 + 1.5 * (q3 - q1)
inside = [a for a in amount if a <= fence]
lo, hi = min(inside), max(inside)
outs = sorted(a for a in amount if a > fence)
W, H, ax = 960, 470, 70
k = 840 / 420  # 1 сумма = 2 пикселя, ось 0..420
X = lambda v: ax + v * k
y0 = 190
b = text(W / 2, 42, "Ящик с усами: суммы заказов", 24, anchor="middle", weight="bold")
b += f'<line x1="{X(lo)}" y1="{y0}" x2="{X(q1)}" y2="{y0}" stroke="{INK}" stroke-width="3"/>'
b += f'<line x1="{X(q3)}" y1="{y0}" x2="{X(hi)}" y2="{y0}" stroke="{INK}" stroke-width="3"/>'
for v in (lo, hi):
    b += f'<line x1="{X(v)}" y1="{y0 - 18}" x2="{X(v)}" y2="{y0 + 18}" stroke="{INK}" stroke-width="3"/>'
b += f'<rect x="{X(q1)}" y="{y0 - 38}" width="{X(q3) - X(q1)}" height="76" fill="{BLUE}" stroke="{BLUE_D}" stroke-width="3"/>'
b += f'<line x1="{X(q2)}" y1="{y0 - 38}" x2="{X(q2)}" y2="{y0 + 38}" stroke="{GREEN}" stroke-width="6"/>'
jit = random.Random(5)  # небольшой разброс по вертикали, чтобы кружки выбросов не слипались
for o in outs:
    if o <= 420:
        b += f'<circle cx="{X(o):.1f}" cy="{y0 + jit.uniform(-24, 24):.1f}" r="6" fill="{RED}" fill-opacity="0.18" stroke="{RED}" stroke-width="2"/>'
b += f'<line x1="{X(fence)}" y1="{y0 - 70}" x2="{X(fence)}" y2="{y0 + 70}" stroke="{RED}" stroke-width="3" stroke-dasharray="8 6"/>'
b += text(X(fence) + 10, y0 - 76, f"граница выбросов {fence:.0f}", 18, RED, "start", "bold")
b += text(X(q1) - 8, y0 - 54, f"Q1 {q1:.0f}", 18, INK, "end", "bold")
b += text(X(q3) + 8, y0 - 54, f"Q3 {q3:.0f}", 18, INK, "start", "bold")
b += text(X(q2), y0 + 74, f"медиана {q2:.0f}", 18, GREEN, "middle", "bold")
ay = 320
b += f'<line x1="{ax}" y1="{ay}" x2="{ax + 840}" y2="{ay}" stroke="{INK}" stroke-width="2"/>'
for v in (0, 100, 200, 300, 400):
    b += f'<line x1="{X(v)}" y1="{ay}" x2="{X(v)}" y2="{ay + 7}" stroke="{INK}" stroke-width="2"/>'
    b += text(X(v), ay + 32, str(v), 18, GRAY, "middle")
b += text(ax + 420, ay + 62, "сумма заказа", 18, GRAY, "middle")
b += text(W / 2, 425, f"IQR = Q3 − Q1 = {q3 - q1:.0f}. Граница выбросов = Q3 + 1,5 × IQR = {fence:.0f}", 18, GRAY, "middle")
b += text(W / 2, 452, f"Каждый красный кружок — один заказ-выброс. Ещё {len([o for o in outs if o > 420])} выбросов дороже 420 (до 4 493) не поместились", 18, RED, "middle")
save("boxplot.svg", W, H, "Ящик с усами для сумм заказов с выбросами", b)

# 4. Корреляция ----------------------------------------------------------------
daily = table("daily.csv")
spend = [float(r["ad_spend"]) for r in daily]
rnd = random.Random(3)
neg = [-(v - 600) * 0.01 + rnd.gauss(0, 0.8) for v in spend]
panels = [
    ("r = +0,98", spend, [float(r["visits"]) for r in daily], "затраты на рекламу → визиты", "визиты", GREEN),
    ("r ≈ 0", spend, [float(r["support_tickets"]) for r in daily], "затраты на рекламу → тикеты", "тикеты", GRAY),
    ("r = −0,9 (пример)", spend, neg, "учебный пример", "значение Y", RED),
]
W, H, pw, ph = 960, 460, 280, 260
b = text(W / 2, 42, "Корреляция: три формы связи двух величин", 24, anchor="middle", weight="bold")
for i, (title, xs, ys, sub, ylab, col) in enumerate(panels):
    ox, oy = 50 + i * 305, 80
    b += f'<line x1="{ox}" y1="{oy}" x2="{ox}" y2="{oy + ph}" stroke="{LINE}" stroke-width="2"/>'
    b += f'<line x1="{ox}" y1="{oy + ph}" x2="{ox + pw}" y2="{oy + ph}" stroke="{LINE}" stroke-width="2"/>'
    lx, hx, ly, hy = min(xs), max(xs), min(ys), max(ys)
    for x, y in zip(xs, ys):
        b += f'<circle cx="{ox + 12 + (x - lx) / (hx - lx) * (pw - 24):.1f}" cy="{oy + ph - 12 - (y - ly) / (hy - ly) * (ph - 24):.1f}" r="4.5" fill="{col}" fill-opacity="0.55"/>'
    b += text(ox - 14, oy + ph / 2, ylab, 16, GRAY, "middle", rotate=-90)
    b += text(ox + pw / 2, oy + ph + 26, "затраты на рекламу" if i < 2 else "значение X", 16, GRAY, "middle")
    b += text(ox + pw / 2, oy + ph + 62, title, 24, col, "middle", "bold")
    b += text(ox + pw / 2, oy + ph + 90, sub, 16, GRAY, "middle")
save("correlation.svg", W, H, "Три графика рассеяния: сильная положительная, нулевая и отрицательная корреляция", b)
