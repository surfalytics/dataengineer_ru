"""Глава 7: калькулятор памяти GPU для inference и finetuning.
Считает по формулам главы: веса, gradients, optimizer states. Activations и KV cache не считаем точно:
для inference берём запас 20%, для training показываем сумму без activations.
Запуск: python3 -I scripts/ai-engineering-code/ch07_memory_calculator.py   (только стандартная библиотека)"""

GB = 1e9  # как в книге: 13 млрд параметров × 2 байта = 26 ГБ

BYTES = {"fp32": 4, "fp16": 2, "bf16": 2, "int8": 1, "int4": 0.5}
# сколько значений на trainable-параметр хранит optimizer (кроме gradient)
OPT_STATES = {"sgd": 0, "momentum": 1, "adam": 2}


def inference_gb(n_params, fmt="fp16", overhead=0.2):
    """N × M × 1.2: веса плюс 20% на activations и key-value векторы."""
    return n_params * BYTES[fmt] * (1 + overhead) / GB


def training_parts(n_params, n_trainable, weights_fmt="fp16", train_fmt="fp16", optimizer="adam"):
    """Память в ГБ по частям: веса, gradients, optimizer states. Activations не включены."""
    weights = n_params * BYTES[weights_fmt] / GB
    grads = n_trainable * BYTES[train_fmt] / GB
    states = n_trainable * OPT_STATES[optimizer] * BYTES[train_fmt] / GB
    return {"веса": weights, "gradients": grads, "optimizer": states, "всего": weights + grads + states}


def lora_params(n_layers, d_model, rank, matrices=4):
    """Сколько trainable-параметров у LoRA: для каждой матрицы d×d это A (d×r) и B (r×d)."""
    return n_layers * matrices * 2 * d_model * rank


def fits(total_gb, gpus=(24, 48, 80)):
    return " ".join(f"{g}ГБ:{'да' if total_gb <= g else 'нет'}" for g in gpus)


print("== 1. Inference: память на веса и с запасом 20% (формула N × M × 1.2)")
print(f"{'модель':>6} {'формат':>6} {'веса, ГБ':>9} {'с запасом, ГБ':>14}")
for name, n in [("7B", 7e9), ("13B", 13e9), ("70B", 70e9)]:
    for fmt in ["fp32", "fp16", "int8", "int4"]:
        w = n * BYTES[fmt] / GB
        print(f"{name:>6} {fmt:>6} {w:>9.1f} {inference_gb(n, fmt):>14.1f}")

print("\n== 2. Gradients и Adam: три значения на каждый trainable-параметр")
for label, trainable in [("13B, все параметры trainable", 13e9), ("1B trainable", 1e9)]:
    g = training_parts(13e9, trainable)
    print(f"{label}: gradients + optimizer = {g['gradients'] + g['optimizer']:.0f} ГБ (3 × 2 байта на параметр)")

print("\n== 3. Модель 7B: полный finetuning и его варианты (fp16/bf16, без activations)")
N = 7e9
lora_8 = lora_params(32, 4096, 8)          # LoRA r=8 на 4 матрицах attention, 32 слоя, d=4096
last_layer = N / 32                        # partial: учим только последний из 32 слоёв (грубо, N/32)
rows = [
    ("полный finetuning, Adam, fp16", training_parts(N, N, "fp16", "fp16", "adam")),
    ("полный finetuning, Adam, fp32", training_parts(N, N, "fp32", "fp32", "adam")),
    ("полный finetuning, SGD без состояния", training_parts(N, N, "fp16", "fp16", "sgd")),
    ("partial: учим 1 слой из 32", training_parts(N, last_layer, "fp16", "fp16", "adam")),
    (f"LoRA r=8 ({lora_8 / 1e6:.1f}M trainable)", training_parts(N, lora_8, "fp16", "fp16", "adam")),
    (f"QLoRA: веса int4 + LoRA r=8", training_parts(N, lora_8, "int4", "fp16", "adam")),
]
print(f"{'способ':<40} {'веса':>6} {'grad':>6} {'opt':>6} {'всего':>7}  помещается")
for label, p in rows:
    print(f"{label:<40} {p['веса']:>6.1f} {p['gradients']:>6.2f} {p['optimizer']:>6.2f} {p['всего']:>7.1f}  {fits(p['всего'])}")

print("\n== 4. Большая модель: 65B / 70B на одной GPU")
for name, n, layers, d in [("65B (Llama-1)", 65e9, 80, 8192), ("70B (Llama-2)", 70e9, 80, 8192)]:
    lp = lora_params(layers, d, 8)
    full = training_parts(n, n, "fp16", "fp16", "adam")
    lora16 = training_parts(n, lp, "fp16", "fp16", "adam")
    q = training_parts(n, lp, "int4", "fp16", "adam")
    print(f"{name}: полный = {full['всего']:.0f} ГБ, LoRA fp16 = {lora16['всего']:.0f} ГБ, "
          f"QLoRA = {q['всего']:.1f} ГБ ({fits(q['всего'])})")

print("\n== 5. Самая большая модель для inference на GPU (с запасом 20%)")
for gpu in (24, 48, 80):
    cells = []
    for fmt in ["fp16", "int8", "int4"]:
        biggest = gpu * GB / (BYTES[fmt] * 1.2) / 1e9
        cells.append(f"{fmt}: {biggest:.0f}B")
    print(f"GPU {gpu} ГБ -> " + ", ".join(cells))

print("\n== 6. Сколько GPU по 80 ГБ нужно для полного finetuning (Adam, fp16, без activations)")
for name, n in [("7B", 7e9), ("13B", 13e9), ("70B", 70e9)]:
    total = training_parts(n, n)["всего"]
    print(f"{name}: {total:.0f} ГБ -> минимум {-(-total // 80):.0f} GPU по 80 ГБ")
