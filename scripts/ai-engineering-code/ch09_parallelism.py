"""Глава 9: replica, tensor и pipeline parallelism на маленьких числах.
1) tensor parallelism: матрицу делим по столбцам между двумя «устройствами», результат тот же;
2) pipeline parallelism: расписание micro-batch на 4 устройствах и доля простоя;
3) replica parallelism: упаковка копий моделей в GPU разного размера (bin packing).
Времена в п. 2 и 3 условные: единицы времени и доля памяти под KV cache придуманы нами.
Запуск: python3 scripts/ai-engineering-code/ch09_parallelism.py   (только стандартная библиотека)"""
import math
import random

print("== 1. Tensor parallelism: A (4x6) * B (6x4), B делим по столбцам между двумя устройствами")
rng = random.Random(2)
A = [[rng.randint(-3, 3) for _ in range(6)] for _ in range(4)]
B = [[rng.randint(-3, 3) for _ in range(4)] for _ in range(6)]


def matmul(x, y):
    return [[sum(x[i][k] * y[k][j] for k in range(len(y))) for j in range(len(y[0]))] for i in range(len(x))]


whole = matmul(A, B)
left = [row[:2] for row in B]            # устройство 1 держит столбцы 0-1
right = [row[2:] for row in B]           # устройство 2 держит столбцы 2-3
part1, part2 = matmul(A, left), matmul(A, right)          # каждое считает свою половину независимо
gathered = [r1 + r2 for r1, r2 in zip(part1, part2)]      # gather: склеиваем столбцы результата
print("результат на одном устройстве и после gather совпал:", whole == gathered)
print(f"умножений на устройство: {4 * 6 * 4} -> {4 * 6 * 2} на каждом из двух; плюс передача результата между устройствами")

print("\nlatency одного слоя: работа делится на T устройств, но связь добавляет плату (условно 0,05 за каждое доп. устройство)")
for t in (1, 2, 4, 8, 16):
    cost = 1 / t + 0.05 * (t - 1)
    print(f"T = {t:>2}: {cost:.3f}")
print("Сначала latency падает, потом растёт: связь съедает выигрыш. Поэтому tensor parallelism обычно держат внутри одной машины.")

print("\n== 2. Pipeline parallelism: 4 устройства, batch разбит на micro-batch")
S = 4
print("Расписание для 4 micro-batch (строка = устройство, колонка = момент времени, цифра = номер micro-batch, . = простой)")
M = 4
for d in range(S):
    row = ""
    for t in range(M + S - 1):
        m = t - d
        row += f"{m + 1:>3}" if 0 <= m < M else "  ."
    print(f"устройство {d + 1}:{row}")
print(f"\n{'micro-batch':>12}{'моментов времени':>18}{'занятость устройств':>21}")
for m in (1, 4, 8, 16, 64):
    slots = m + S - 1
    print(f"{m:>12}{slots:>18}{m / slots:>21.0%}")
print("Чем больше micro-batch, тем меньше простоя в начале и конце. Но один запрос всё равно идёт через 4 устройства подряд.")
hop = 0.1  # условная плата за передачу между устройствами
print(f"latency одного запроса: на одном устройстве {S * 1.0:.1f}, в pipeline из {S} стадий {S * 1.0 + (S - 1) * hop:.1f} (плата за {S - 1} передачи)")

print("\n== 3. Replica parallelism: упаковка копий моделей в GPU")
gpus = {"GPU-80": 80, "GPU-48": 48, "GPU-40": 40, "GPU-24a": 24, "GPU-24b": 24}   # GB
wanted = [("70B", 70), ("34B", 34), ("13B", 13), ("13B", 13), ("13B", 13), ("8B", 8), ("8B", 8)]  # 8 бит: 1 байт на параметр


def pack(reserve):
    """Best fit decreasing: самую большую копию кладём в GPU, где останется меньше всего места."""
    free = {g: size * (1 - reserve) for g, size in gpus.items()}
    placed = {g: [] for g in gpus}
    lost = []
    for name, gb in sorted(wanted, key=lambda x: -x[1]):
        fits = [g for g in free if free[g] >= gb]
        if not fits:
            lost.append(name)
            continue
        g = min(fits, key=lambda g: free[g] - gb)
        free[g] -= gb
        placed[g].append(name)
    return placed, lost


print("Нужны копии: " + ", ".join(n for n, _ in wanted) + " (веса в 8 бит, GB = млрд параметров)")
for reserve in (0.0, 0.2):
    placed, lost = pack(reserve)
    print(f"\nрезерв под KV cache и активации: {reserve:.0%}")
    for g, names in placed.items():
        print(f"  {g:<8} ({gpus[g]} GB): {', '.join(names) or 'пусто'}")
    print(f"  не поместились: {', '.join(lost) or 'нет'}")
print(f"\nСколько копий 13B помещается в GPU на 40 GB: без резерва {int(40 // 13)}, с резервом 20% {int(40 * 0.8 // 13)}.")
print("Три копии 13B (39 GB) 'влезают' в 40 GB только без места под KV cache. С резервом остаются две.")
print("Модель 70B (70 GB в 8 бит) при резерве 20% не помещается даже в GPU на 80 GB: её надо делить между GPU (model parallelism).")
