"""Глава 2: размер модели. Считаем число параметров transformer по его размерностям (d_model, d_ff, слои, словарь),
проверяем память для inference, MoE (всего и активных параметров) и размер KV cache.
Конфигурации Llama и Mixtral взяты из их открытых config-файлов.
Запуск: python3 -I scripts/ai-engineering-code/ch02_model_size.py   (только стандартная библиотека)"""

# blocks — число transformer-блоков, d — d_model, ff — d_ff, vocab — словарь,
# heads / kv_heads — головы attention (kv_heads < heads значит grouped-query attention),
# experts / active — число экспертов MoE и сколько из них работает на токен
MODELS = {
    "Llama 2-7B": dict(blocks=32, d=4096, ff=11008, vocab=32000, heads=32, kv_heads=32),
    "Llama 2-13B": dict(blocks=40, d=5120, ff=13824, vocab=32000, heads=40, kv_heads=40),
    "Llama 2-70B": dict(blocks=80, d=8192, ff=28672, vocab=32000, heads=64, kv_heads=8),
    "Llama 3-8B": dict(blocks=32, d=4096, ff=14336, vocab=128256, heads=32, kv_heads=8),
    "Llama 3-70B": dict(blocks=80, d=8192, ff=28672, vocab=128256, heads=64, kv_heads=8),
    "Llama 3-405B": dict(blocks=126, d=16384, ff=53248, vocab=128256, heads=128, kv_heads=8),
    "Mixtral 8x7B": dict(blocks=32, d=4096, ff=14336, vocab=32000, heads=32, kv_heads=8, experts=8, active=2),
}


def params(c, mlp_matrices=3):
    """Возвращает (всего параметров, активных на токен). Нормализации и router не считаем: их доля ничтожна."""
    kv_dim = c["d"] * c["kv_heads"] // c["heads"]
    attn = 2 * c["d"] * c["d"] + 2 * c["d"] * kv_dim  # Q и O: d×d; K и V: d×kv_dim
    mlp = mlp_matrices * c["d"] * c["ff"]  # у Llama «gated» MLP: три матрицы вместо двух на схеме книги
    experts, active = c.get("experts", 1), c.get("active", 1)
    emb = 2 * c["vocab"] * c["d"]  # embedding на входе и unembedding на выходе
    total = c["blocks"] * (attn + experts * mlp) + emb
    act = c["blocks"] * (attn + active * mlp) + emb
    return total, act


print("== 1. Параметры из размерностей (формулы выше, расчёт нашего скрипта)")
print(f"{'модель':14s} {'всего':>9s} {'активных':>9s}")
for name, c in MODELS.items():
    total, act = params(c)
    print(f"{name:14s} {total / 1e9:8.1f}B {act / 1e9:8.1f}B")

print("\n== 2. Что если считать MLP из двух матриц, как на схеме книги")
t2, _ = params(MODELS["Llama 2-7B"], mlp_matrices=2)
t3, _ = params(MODELS["Llama 2-7B"], mlp_matrices=3)
print(f"Llama 2-7B: две матрицы -> {t2 / 1e9:.1f}B, три матрицы -> {t3 / 1e9:.1f}B (настоящая Llama использует три)")
bad = dict(MODELS["Llama 2-70B"], ff=22016)
print(f"Llama 2-70B с d_ff = 22016 (число из таблицы книги): {params(bad)[0] / 1e9:.1f}B, с d_ff = 28672: {params(MODELS['Llama 2-70B'])[0] / 1e9:.1f}B")

print("\n== 3. Память для inference: параметры × байт на параметр")
for bits, label in [(16, "16 бит (2 байта)"), (8, "8 бит"), (4, "4 бита")]:
    print(f"7B параметров, {label:17s}: {7e9 * bits / 8 / 1e9:5.1f} GB")
print("это минимум только для весов, на практике нужно больше (KV cache, активации)")

print("\n== 4. MoE: Mixtral 8x7B")
total, act = params(MODELS["Mixtral 8x7B"])
print(f"если эксперты не делят параметры: 8 × 7B = 56B; на деле всего {total / 1e9:.1f}B (общие слои attention и embedding)")
print(f"на токен работают 2 эксперта из 8: {act / 1e9:.1f}B активных -> цена и скорость как у модели на {act / 1e9:.1f}B")
print(f"доля активных параметров: {act / total:.0%}")

print("\n== 5. KV cache: сколько памяти на токен (16 бит): 2 (K и V) × блоки × kv_dim × 2 байта")
for name in ["Llama 2-7B", "Llama 3-8B", "Llama 3-70B"]:
    c = MODELS[name]
    kv_dim = c["d"] * c["kv_heads"] // c["heads"]
    per_token = 2 * c["blocks"] * kv_dim * 2
    print(f"{name:12s} {per_token / 1024:6.0f} KB на токен; 4K токенов = {per_token * 4096 / 2 ** 30:5.1f} GiB, 128K токенов = {per_token * 131072 / 2 ** 30:6.1f} GiB")
print("чем длиннее контекст, тем больше кэш; grouped-query attention (kv_heads < heads) уменьшает его")

print("\n== 6. Три порядка роста параметров")
print(f"GPT-1 117M -> GPT-2 1,5B: ×{1.5e9 / 117e6:.0f}; GPT-2 -> GPT-3 175B: ×{175e9 / 1.5e9:.0f}; GPT-1 -> GPT-3: ×{175e9 / 117e6:.0f}")
print(f"ещё три порядка от GPT-3: {175e9 * 1e3 / 1e12:.0f} трлн параметров (книга округляет до 100 трлн)")
