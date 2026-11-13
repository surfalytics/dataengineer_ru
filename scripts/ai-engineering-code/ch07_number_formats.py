"""Глава 7: числовые форматы (FP32, FP16, BF16, TF32) и quantization до INT8 / INT4.
Показывает: сколько бит на диапазон и точность, как округляются значения, что ломается при
неверном формате, как работает простая quantization и почему выброс (outlier) портит её.
Запуск: python3 -I scripts/ai-engineering-code/ch07_number_formats.py   (только стандартная библиотека)"""
import math
import random
import struct

INF = float("inf")


def to_fp32(x):
    return struct.unpack("f", struct.pack("f", x))[0]


def to_fp16(x):
    if abs(x) >= 65520:          # за пределом диапазона FP16: бесконечность
        return math.copysign(INF, x)
    return struct.unpack("e", struct.pack("e", x))[0]


def _drop_mantissa(x, drop):
    """Округляет FP32 до формата с меньшей мантиссой: отбрасываем `drop` младших бит (round-to-nearest-even)."""
    bits = struct.unpack("I", struct.pack("f", to_fp32(x)))[0]
    lsb = (bits >> drop) & 1
    bits = (bits + (1 << (drop - 1)) - 1 + lsb) & ~((1 << drop) - 1) & 0xFFFFFFFF
    return struct.unpack("f", struct.pack("I", bits))[0]


def to_bf16(x):
    return _drop_mantissa(x, 16)   # 8 бит экспоненты, 7 бит мантиссы


def to_tf32(x):
    return _drop_mantissa(x, 13)   # 8 бит экспоненты, 10 бит мантиссы


FORMATS = [("FP32", 8, 23), ("FP16", 5, 10), ("BF16", 8, 7), ("TF32", 8, 10)]

print("== 1. Из чего состоит формат: 1 бит знака + биты диапазона (exponent) + биты точности (mantissa)")
print(f"{'формат':>6} {'range':>6} {'precision':>10} {'бит':>4} {'байт':>5} {'max значение':>14} {'шаг точности':>13}")
for name, e, m in FORMATS:
    bits = 1 + e + m
    biggest = (2 - 2 ** -m) * 2 ** (2 ** (e - 1) - 1)
    print(f"{name:>6} {e:>6} {m:>10} {bits:>4} {bits / 8:>5.2f} {biggest:>14.5g} {2 ** -m:>13.2e}")
print("TF32 занимает 19 бит, а не 32: имя говорит о совместимости с FP32, а не о размере.")

print("\n== 2. Округление значений FP32 в форматы с меньшей точностью (относительная ошибка в %)")
print(f"{'FP32':>12} | {'FP16':>12} {'ошибка':>8} | {'BF16':>12} {'ошибка':>8} | {'TF32':>12} {'ошибка':>8}")
for x in [0.00314159, 0.314159, 3.14159, 314.159, 3141.59, 31415.9, 314159.0, 3141590.0]:
    cells = []
    for f in (to_fp16, to_bf16, to_tf32):
        y = f(x)
        err = "—" if math.isinf(y) else f"{abs(y - x) / x * 100:.3f}%"
        cells.append(f"{y:>12.8g} {err:>8}")
    print(f"{x:>12.8g} | " + " | ".join(cells))
print("Выше 65504 FP16 даёт inf. BF16 держит большие числа, но округляет грубее, чем FP16.")

print("\n== 3. Ловушка: веса сохранены в BF16, а мы загрузили их в FP16")
rng = random.Random(7)
weights = [rng.gauss(0, 0.02) for _ in range(10000)]
big_values = [1.2e5, -9.0e4, 7.5e4, 1.0e5, -2.0e5]   # редкие огромные значения, как у activations
tiny_values = [1e-9, -3e-9, 2e-10]                  # очень маленькие значения
all_values = weights + big_values + tiny_values
bf = [to_bf16(v) for v in all_values]               # так модель хранится
as_fp16 = [to_fp16(v) for v in bf]                  # так мы её ошибочно загрузили
overflow = sum(1 for v in as_fp16 if math.isinf(v))
underflow = sum(1 for v, o in zip(as_fp16, bf) if v == 0 and o != 0)
rel16 = sum(abs(to_fp16(v) - v) / abs(v) for v in weights) / len(weights) * 100
rel_bf = sum(abs(to_bf16(v) - v) / abs(v) for v in weights) / len(weights) * 100
print(f"значений: {len(all_values)}; после загрузки в FP16: стало inf = {overflow}, стало 0 = {underflow}")
print(f"средняя ошибка округления на обычных весах: FP16 {rel16:.3f}%, BF16 {rel_bf:.3f}%")
print("Вывод: у FP16 точнее мелкие значения, но диапазон узкий. Один inf портит весь слой.")


def quant_absmax(values, levels):
    """Симметричная quantization: scale = max|x| / levels, q = round(x / scale), обратно q × scale."""
    scale = max(abs(v) for v in values) / levels
    return [round(v / scale) * scale for v in values], scale


def quant_blocks(values, levels, block):
    out = []
    for i in range(0, len(values), block):
        q, _ = quant_absmax(values[i:i + block], levels)
        out.extend(q)
    return out


def mean_abs_err(a, b):
    return sum(abs(x - y) for x, y in zip(a, b)) / len(a)


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def output_error(w_true, w_quant, inputs):
    """Относительная ошибка выхода слоя: RMS(q·x − w·x) / RMS(w·x) по набору входов."""
    diffs = [dot(w_quant, x) - dot(w_true, x) for x in inputs]
    refs = [dot(w_true, x) for x in inputs]
    rms = lambda v: math.sqrt(sum(a * a for a in v) / len(v))
    return rms(diffs) / rms(refs) * 100


print("\n== 4. Quantization весов в INT8 и INT4 (255 и 15 уровней вместо миллиардов)")
rng = random.Random(11)
w = [rng.gauss(0, 0.02) for _ in range(512)]
inputs = [[rng.gauss(0, 1.0) for _ in range(512)] for _ in range(200)]
print(f"{'формат':<8} {'ср. ошибка веса':>16} {'ошибка выхода слоя':>20} {'байт на вес':>12}")
for name, levels, size in [("INT8", 127, 1), ("INT4", 7, 0.5)]:
    q, scale = quant_absmax(w, levels)
    print(f"{name:<8} {mean_abs_err(w, q):>16.6f} {output_error(w, q, inputs):>19.2f}% {size:>12}")

print("\n== 5. Один выброс (outlier) портит общий scale. Блоки по 32 значения помогают")
w_out = list(w)
w_out[100] = 1.0            # один вес в 50 раз больше остальных
normal = [i for i in range(len(w)) if i != 100]
print(f"{'способ':<28} {'ошибка обычных весов':>21} {'ошибка выхода слоя':>20}")
for label, q in [
    ("INT8, один scale", quant_absmax(w_out, 127)[0]),
    ("INT8, scale на блок 32", quant_blocks(w_out, 127, 32)),
    ("INT4, один scale", quant_absmax(w_out, 7)[0]),
    ("INT4, scale на блок 32", quant_blocks(w_out, 7, 32)),
]:
    err_normal = mean_abs_err([w_out[i] for i in normal], [q[i] for i in normal])
    print(f"{label:<28} {err_normal:>21.6f} {output_error(w_out, q, inputs):>19.2f}%")

print("\n== 6. Сколько памяти занимает модель 7B при разном числе бит на вес")
for label, bits in [("FP32", 32), ("FP16 / BF16", 16), ("INT8", 8), ("INT4", 4), ("тернарный (1.58 бита)", math.log2(3))]:
    print(f"{label:<24} {bits:>5.2f} бита на вес -> {7e9 * bits / 8 / 1e9:>6.2f} ГБ")
ternary_scale = sum(abs(v) for v in w) / len(w)
ternary = [max(-1, min(1, round(v / ternary_scale))) for v in w]
share = {s: ternary.count(s) / len(ternary) for s in (-1, 0, 1)}
print("тернарная quantization весов (-1, 0, +1): " + ", ".join(f"{s:+d}: {p:.0%}" for s, p in share.items()))
