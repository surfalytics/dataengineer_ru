"""Глава 2: FLOPs, стоимость обучения и scaling law Chinchilla. Считаем время и деньги для GPT-3,
проверяем правило C ≈ 6·N·D (это известная оценка из работ про scaling laws, в книге её нет),
находим compute-optimal размер модели и число токенов под бюджет.
Запуск: python3 -I scripts/ai-engineering-code/ch02_compute_scaling.py   (только стандартная библиотека)"""
import math

print("== 1. FLOPs и FLOP/s: работа и скорость")
h100_flops_per_s = 60e12  # 60 TFLOP/s, пик H100 по данным книги
per_day = h100_flops_per_s * 86_400
print(f"H100: {h100_flops_per_s:.1e} FLOP/s = {per_day:.2e} FLOPs в сутки (в книге округлено до 5,2e18)")
print("1 FLOP/s-день = 60 × 60 × 24 =", 60 * 60 * 24, "FLOPs")

print("\n== 2. Сколько обучать GPT-3 175B на 256 H100 (3,14e23 FLOPs)")
gpt3_flops = 3.14e23
gpus, per_day_book = 256, 5.2e18
days_ideal = gpt3_flops / (gpus * per_day_book)
print(f"при 100% загрузке: {days_ideal:.0f} суток = {days_ideal / 30.4:.1f} месяца")
for util in (1.0, 0.7, 0.5):
    days = days_ideal / util
    cost = 2 * gpus * 24 * days  # $2 за GPU-час
    print(f"загрузка {util:4.0%}: {days:4.0f} суток, при $2/ч стоит ${cost:,.0f}; при $5/ч ${cost * 2.5:,.0f}")
print(f"если округлить до 236 суток, как в книге, при 70% и $2/ч: ${2 * gpus * 24 * 236 / 0.7:,.0f}")

print("\n== 3. Правило C ≈ 6·N·D (N параметров, D токенов обучения)")
rows = [("LaMDA", 137e9, 168e9), ("GPT-3", 175e9, 300e9), ("Jurassic", 178e9, 300e9), ("Gopher", 280e9, 300e9),
        ("MT-NLG", 530e9, 270e9), ("Chinchilla", 70e9, 1.4e12)]
print(f"{'модель':11s} {'параметры':>10s} {'токены':>9s} {'токенов на параметр':>20s}")
for name, n, d in rows:
    print(f"{name:11s} {n / 1e9:9.0f}B {d / 1e9:8.0f}B {d / n:20.1f}")
print(f"6·N·D для GPT-3: {6 * 175e9 * 300e9:.2e} FLOPs (по отчёту: 3,14e23)")

print("\n== 4. Compute-optimal по Chinchilla: D = 20·N и C = 6·N·D  =>  N = sqrt(C / 120)")
for label, c in [("3B-модель из книги", 6 * 3e9 * 60e9), ("бюджет 1e21", 1e21), ("бюджет GPT-3", gpt3_flops), ("бюджет около 5,8e23", 5.76e23)]:
    n = math.sqrt(c / 120)
    print(f"{label:21s} C = {c:.2e}: N = {n / 1e9:5.1f}B, D = {20 * n / 1e9:7.1f}B токенов")
print("для бюджета около 5,8e23 получаем 69B и 1,4T: это Chinchilla (70B параметров, 1,4T токенов)")

print("\n== 5. Модель, обученная «сверх» оптимума, ради дешёвого inference")
n, d = 8e9, 15e12
print(f"Llama 3-8B: {d / 1e12:.0f}T токенов на {n / 1e9:.0f}B параметров = {d / n:.0f} токенов на параметр (оптимум Chinchilla: 20)")

print("\n== 6. Токены датасета и токены обучения")
dataset_tokens, epochs = 1e12, 2
print(f"датасет {dataset_tokens / 1e12:.0f}T токенов, {epochs} эпохи -> токенов обучения: {dataset_tokens * epochs / 1e12:.0f}T")
books = 30e12 / 67_000
print(f"RedPajama-v2: 30T токенов / 67 000 токенов в книге = {books / 1e6:.0f} млн книг")

print("\n== 7. Сколько комбинаций гиперпараметров")
print("10 гиперпараметров по одному, парам, тройкам и так далее:", sum(math.comb(10, k) for k in range(11)), "комбинаций (с пустой)")
