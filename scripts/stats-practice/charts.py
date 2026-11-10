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


BLUE, BLUE_D, RED, GREEN, GRAY, INK = "#a5d8ff", "#1971c2", "#e03131", "#2f9e44", "#868e96", "#1e1e1e"
FONT = "font-family=\"system-ui, -apple-system, 'Segoe UI', sans-serif\""


def svg(w, h, title, body):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{title}">'
        f'<rect width="{w}" height="{h}" fill="#ffffff"/>{body}</svg>'
    )


def text(x, y, s, size=16, color=INK, anchor="start", weight="normal"):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}" {FONT}>{s}</text>'


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
x0, base, bw = 60, 300, 28
scale = 190 / max(bins)
b = text(320, 30, "Суммы заказов: большие заказы тянут среднее вправо", 18, anchor="middle", weight="bold")
for i, n in enumerate(bins):
    hgt = n * scale
    b += f'<rect x="{x0 + i * bw}" y="{base - hgt}" width="{bw - 2}" height="{hgt}" fill="{BLUE}" stroke="{BLUE_D}"/>'
b += f'<line x1="{x0}" y1="{base}" x2="{x0 + 20 * bw}" y2="{base}" stroke="{INK}" stroke-width="2"/>'
for v in (0, 100, 200, 300, 400):
    b += text(x0 + v / 20 * bw, base + 20, str(v), 14, GRAY, "middle")
b += text(x0 + 10 * bw, base + 44, "сумма заказа", 15, GRAY, "middle")
for val, label, col, dy in ((med, f"медиана {med:.0f}", GREEN, 0), (mean, f"среднее {mean:.0f}", RED, 0)):
    x = x0 + val / 20 * bw
    b += f'<line x1="{x}" y1="70" x2="{x}" y2="{base}" stroke="{col}" stroke-width="3" stroke-dasharray="7 5"/>'
    b += text(x + (-8 if col == GREEN else 8), 68, label, 16, col, "end" if col == GREEN else "start", "bold")
b += text(x0 + 20 * bw, 150, f"ещё {big} заказов", 15, RED, "end")
b += text(x0 + 20 * bw, 170, "дороже 400 (до 4 493)", 15, RED, "end")
save("mean-vs-median.svg", 640, 370, "Гистограмма сумм заказов. Среднее правее медианы", b)

# 2. Нормальное распределение -------------------------------------------------
d = [float(r["delivery_hours"]) for r in table("orders.csv")]
m, s = st.mean(d), st.stdev(d)
W, H, bx, by, sx = 640, 350, 40, 260, 70  # sx — пикселей на одно s
pdf = lambda z: math.exp(-z * z / 2) / math.sqrt(2 * math.pi)
yy = lambda z: by - pdf(z) * 520
b = text(W / 2, 28, "Нормальное распределение: время доставки (часы)", 20, anchor="middle", weight="bold")
cx = W / 2
for k, col, label in ((3, "#e7f5ff", "99,7%"), (2, "#d0ebff", "95%"), (1, BLUE, "68%")):
    pts = [(-k + i * 2 * k / 60) for i in range(61)]
    poly = " ".join(f"{cx + z * sx:.1f},{yy(z):.1f}" for z in pts)
    b += f'<polygon points="{cx - k * sx},{by} {poly} {cx + k * sx},{by}" fill="{col}"/>'
curve = " ".join(f"{cx + z * sx:.1f},{yy(z):.1f}" for z in [(-3.5 + i * 7 / 100) for i in range(101)])
b += f'<polyline points="{curve}" fill="none" stroke="{BLUE_D}" stroke-width="3"/>'
b += f'<line x1="{bx}" y1="{by}" x2="{W - bx}" y2="{by}" stroke="{INK}" stroke-width="2"/>'
for k in range(-3, 4):
    b += f'<line x1="{cx + k * sx}" y1="{by}" x2="{cx + k * sx}" y2="{by + 6}" stroke="{INK}"/>'
    lab = "μ" if k == 0 else (f"μ{k:+d}σ".replace("+1σ", "+σ").replace("-1σ", "−σ").replace("-", "−"))
    b += text(cx + k * sx, by + 24, lab, 15, INK, "middle")
    b += text(cx + k * sx, by + 44, f"{m + k * s:.0f} ч", 14, GRAY, "middle")
for k, label, yl in ((1, "68% данных: ±1σ", 150), (2, "95%: ±2σ", 215), (3, "99,7%: ±3σ", 245)):
    pass
b += text(cx, 175, "68%", 18, BLUE_D, "middle", "bold")
b += text(cx - 1.5 * sx, 232, "95%", 16, BLUE_D, "middle", "bold")
b += text(cx + 1.5 * sx, 232, "95%", 16, BLUE_D, "middle", "bold")
b += text(W / 2, 336, f"μ — среднее ({m:.1f} ч), σ — стандартное отклонение ({s:.1f} ч)", 14, GRAY, "middle")
save("normal-distribution.svg", W, H, "Нормальное распределение: 68, 95 и 99,7 процентов данных", b)

# 3. Boxplot --------------------------------------------------------------------
q1, q2, q3 = st.quantiles(amount, n=4, method="inclusive")
fence = q3 + 1.5 * (q3 - q1)
inside = [a for a in amount if a <= fence]
lo, hi = min(inside), max(inside)
outs = sorted(a for a in amount if a > fence)
W, H, ax, ak = 640, 250, 50, 1.0  # 1 пиксель = 0,5 $... ось 0..560 px = 0..420
k = 540 / 420
X = lambda v: ax + v * k
b = text(W / 2, 28, "Ящик с усами: суммы заказов", 20, anchor="middle", weight="bold")
y0 = 110
b += f'<line x1="{X(lo)}" y1="{y0}" x2="{X(q1)}" y2="{y0}" stroke="{INK}" stroke-width="2"/>'
b += f'<line x1="{X(q3)}" y1="{y0}" x2="{X(hi)}" y2="{y0}" stroke="{INK}" stroke-width="2"/>'
for v in (lo, hi):
    b += f'<line x1="{X(v)}" y1="{y0 - 14}" x2="{X(v)}" y2="{y0 + 14}" stroke="{INK}" stroke-width="2"/>'
b += f'<rect x="{X(q1)}" y="{y0 - 28}" width="{X(q3) - X(q1)}" height="56" fill="{BLUE}" stroke="{BLUE_D}" stroke-width="2"/>'
b += f'<line x1="{X(q2)}" y1="{y0 - 28}" x2="{X(q2)}" y2="{y0 + 28}" stroke="{GREEN}" stroke-width="4"/>'
for o in outs:
    if o <= 420:
        b += f'<circle cx="{X(o)}" cy="{y0}" r="4" fill="none" stroke="{RED}" stroke-width="2"/>'
b += text(W - 20, 140, f"ещё {len([o for o in outs if o > 420])} выбросов дороже 420 (до 4 493)", 14, RED, "end")
b += f'<line x1="{ax}" y1="190" x2="{ax + 540}" y2="190" stroke="{INK}" stroke-width="2"/>'
for v in (0, 100, 200, 300, 400):
    b += text(X(v), 212, str(v), 14, GRAY, "middle")
for v, label, col, yl in ((q1, f"Q1 {q1:.0f}", INK, 62), (q2, f"медиана {q2:.0f}", GREEN, 48), (q3, f"Q3 {q3:.0f}", INK, 62)):
    anchor = "end" if label.startswith("Q1") else ("middle" if label.startswith("мед") else "start")
    b += text(X(v) + (-4 if anchor == "end" else (4 if anchor == "start" else 0)), yl, label, 15, col, anchor, "bold")
b += text(X(fence) + 6, 150, f"граница выбросов {fence:.0f}", 14, RED, "start")
b += f'<line x1="{X(fence)}" y1="{y0 - 20}" x2="{X(fence)}" y2="170" stroke="{RED}" stroke-width="2" stroke-dasharray="5 4"/>'
b += text(X((q1 + q3) / 2), 150, "IQR = Q3 − Q1", 14, BLUE_D, "middle")
b += text(W / 2, 240, "граница выбросов = Q3 + 1,5 × IQR", 14, GRAY, "middle")
save("boxplot.svg", W, H, "Ящик с усами для сумм заказов с выбросами", b)

# 4. Корреляция ----------------------------------------------------------------
daily = table("daily.csv")
spend = [float(r["ad_spend"]) for r in daily]
rnd = random.Random(3)
neg = [-(v - 600) * 0.01 + rnd.gauss(0, 0.8) for v in spend]
panels = [
    ("r = +0,98", spend, [float(r["visits"]) for r in daily], "затраты на рекламу → визиты", GREEN),
    ("r ≈ 0", spend, [float(r["support_tickets"]) for r in daily], "затраты на рекламу → тикеты", GRAY),
    ("r = −0,9 (пример)", spend, neg, "учебный пример", RED),
]
W, H, pw, ph = 900, 330, 260, 200
b = text(W / 2, 28, "Корреляция: три формы связи двух величин", 20, anchor="middle", weight="bold")
for i, (title, xs, ys, sub, col) in enumerate(panels):
    ox, oy = 30 + i * 295, 60
    b += f'<rect x="{ox}" y="{oy}" width="{pw}" height="{ph}" fill="none" stroke="{GRAY}"/>'
    lx, hx, ly, hy = min(xs), max(xs), min(ys), max(ys)
    for x, y in zip(xs, ys):
        b += f'<circle cx="{ox + 10 + (x - lx) / (hx - lx) * (pw - 20):.1f}" cy="{oy + ph - 10 - (y - ly) / (hy - ly) * (ph - 20):.1f}" r="3" fill="{col}" fill-opacity="0.6"/>'
    b += text(ox + pw / 2, oy + ph + 28, title, 18, col, "middle", "bold")
    b += text(ox + pw / 2, oy + ph + 50, sub, 14, GRAY, "middle")
save("correlation.svg", W, H, "Три графика рассеяния: сильная положительная, нулевая и отрицательная корреляция", b)
