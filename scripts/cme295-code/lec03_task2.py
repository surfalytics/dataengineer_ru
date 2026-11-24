"""Задача 2: интерполяция позиций для длинного контекста."""
train_len, new_len = 4096, 131072
scale = new_len / train_len                             # во сколько раз растягиваем

# Частоты четырёх пар измерений RoPE: от быстрой до медленной
freqs = [1.0, 0.1, 0.01, 0.001]
max_seen = [(train_len - 1) * f for f in freqs]         # наибольший угол при обучении на 4096

pos = 100_000
print("масштаб:", scale)
print("позиция после интерполяции:", pos / scale)
for f, seen in zip(freqs, max_seen):
    raw = pos * f
    interp = pos / scale * f
    out_raw = "вне диапазона" if raw > seen else "внутри"
    out_new = "вне диапазона" if interp > seen else "внутри"
    print(f"f={f:<6} без правки {raw:9.1f} ({out_raw}) | с интерполяцией {interp:7.1f} ({out_new})")
