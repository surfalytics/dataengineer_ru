"""Глава 9: MFU, MBU и игрушечная roofline-модель. Почему decode упирается в память, а prefill в вычисления.
Из книги: формулы MFU и MBU, пример 7B в FP16 на A100-80GB (пропускная способность памяти 2 TB/s),
определение arithmetic intensity (операций на байт обращения к памяти), числа PyTorch-кейса (рис. 9-14).
Наши допущения (их нет в книге): пик A100 в FP16 берём 300 TFLOP/s, а на один токен нужно 2 FLOP на параметр.
Запуск: python3 scripts/ai-engineering-code/ch09_mfu_mbu.py   (только стандартная библиотека)"""

PARAMS = 7e9          # модель на 7 млрд параметров
BANDWIDTH = 2e12      # байт/с: A100-80GB, как в книге
PEAK_FLOPS = 300e12   # FLOP/s: наше допущение для A100 в FP16
BYTES = {"FP16": 2, "INT8": 1, "INT4": 0.5}

print("== 1. MFU: наблюдаемый throughput против пикового")
print(f"чип мог бы дать 100 токенов/с на пике FLOP/s, сервис даёт 20 -> MFU = {20 / 100:.0%}")

print("\n== 2. MBU: сколько пропускной способности памяти использует decode")
print("формула: параметры * байт на параметр * токенов в секунду / пропускная способность")
for fmt in ("FP16", "INT8", "INT4"):
    used = PARAMS * BYTES[fmt] * 100          # при 100 токенов/с
    print(f"{fmt}: 7B * {BYTES[fmt]} * 100 = {used / 1e9:,.0f} GB/s -> MBU {used / BANDWIDTH:.0%}".replace(",", " "))
print("Пример книги (7B, FP16, 100 токенов/с): 7B * 2 * 100 = 1 400 GB/s, делим на 2 TB/s -> 70%.")

print("\n== 3. Потолок скорости decode при batch = 1 (MBU = 100%)")
for fmt in ("FP16", "INT8", "INT4"):
    ceiling = BANDWIDTH / (PARAMS * BYTES[fmt])
    print(f"{fmt}: {ceiling:>5.0f} токенов/с")
print("Каждый токен требует прочитать из памяти ВСЕ веса. Меньше байт на параметр -> выше потолок.")

print("\n== 4. PyTorch-кейс (рис. 9-14): те же числа через MBU")
print(f"{'шаг':<22}{'токенов/с':>10}{'байт/парам.':>12}{'MBU':>7}")
steps = [("eager", 25.5, 2), ("torch.compile", 107.0, 2), ("INT8", 157.4, 1), ("INT4", 202.1, 0.5)]
for name, tps, b in steps:
    mbu = PARAMS * b * tps / BANDWIDTH
    print(f"{name:<22}{tps:>10.1f}{b:>12}{mbu:>7.0%}")
print("compile убирает накладные расходы: MBU растёт с 18% до 75%. INT8 и INT4 уменьшают байты:")
print("токенов в секунду больше, хотя MBU ниже. Рост скорости важнее, чем рост MBU.")

print("\n== 5. Roofline: decode при разных размерах batch")
print("Arithmetic intensity = FLOP / байт. Один шаг decode читает веса один раз на весь batch:")
print("FLOP = 2 * параметры * batch, байт = параметры * байт на параметр, значит intensity = 2 * batch / байт на параметр")
ridge = PEAK_FLOPS / BANDWIDTH
print(f"точка перелома (ridge point) = пик FLOP/s / пропускная способность = {ridge:.0f} FLOP/байт")
print(f"{'batch':>6}{'intensity':>11}{'достижимо TFLOP/s':>19}{'MFU':>7}  режим")
for batch in (1, 8, 32, 64, 128, 256, 512):
    inten = 2 * batch / BYTES["FP16"]
    attain = min(PEAK_FLOPS, inten * BANDWIDTH)
    mode = "память (memory-bound)" if inten < ridge else "вычисления (compute-bound)"
    print(f"{batch:>6}{inten:>11.0f}{attain / 1e12:>19.1f}{attain / PEAK_FLOPS:>7.1%}  {mode}")
print("При batch = 1 чип использует меньше 1% своих FLOP/s: он ждёт память. Batching поднимает intensity.")

print("\n== 6. Prefill: промпт обрабатывается пачкой токенов, значит intensity растёт с длиной промпта")
for n in (16, 64, 200, 500, 2000):
    inten = 2 * n / BYTES["FP16"]
    mode = "память" if inten < ridge else "вычисления"
    print(f"промпт {n:>5} токенов: intensity {inten:>5.0f} -> {mode}")
print("Длинный промпт сразу попадает в зону compute-bound, поэтому prefill упирается в FLOP/s.")
