"""Задача 3: докуда видит токен при скользящем окне и нескольких слоях."""
import numpy as np

n, window, layers = 16, 4, 3

# visible[i][j] = True, если токен i смотрит на токен j за один слой
visible = np.zeros((n, n), dtype=bool)
for i in range(n):
    for j in range(max(0, i - window + 1), i + 1):
        visible[i, j] = True

reach = np.eye(n, dtype=bool)
for layer in range(1, layers + 1):
    reach = (reach.astype(int) @ visible.astype(int)) > 0     # шаг назад через ещё один слой
    first = int(np.argmax(reach[n - 1]))
    print(f"после слоя {layer}: последний токен видит позиции с {first} по {n - 1}")
