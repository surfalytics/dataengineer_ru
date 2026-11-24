"""LayerNorm и RMSNorm на одном векторе (gamma = 1, beta = 0)."""
import numpy as np

x = np.array([1.0, 2.0, 3.0, 10.0])
eps = 1e-6

layer = (x - x.mean()) / np.sqrt(x.var() + eps)     # центрируем и масштабируем
rms = x / np.sqrt((x ** 2).mean() + eps)            # только масштабируем

print("x:        ", x.tolist())
print("LayerNorm:", np.round(layer, 3).tolist(), " среднее:", round(float(layer.mean()), 3))
print("RMSNorm:  ", np.round(rms, 3).tolist(), " среднее:", round(float(rms.mean()), 3))
