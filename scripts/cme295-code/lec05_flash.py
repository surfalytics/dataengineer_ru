"""FlashAttention: softmax по блокам даёт тот же ответ, что и обычный, и не ломается на больших числах."""
import numpy as np

rng = np.random.default_rng(5)
n, d = 8, 4
s = rng.normal(0, 5, n)           # оценки внимания одного запроса: q·k для 8 ключей
V = rng.normal(0, 1, (n, d))      # 8 векторов value


def обычное(s, V):
    w = np.exp(s - s.max())       # полная строка сразу
    return (w / w.sum()) @ V


def по_блокам(s, V, блок=2, dtype=np.float64):
    s, V = s.astype(dtype), V.astype(dtype)
    m = dtype(-np.inf)                       # максимум оценок, которые уже видели
    числитель = np.zeros(V.shape[1], dtype)  # сумма exp(s_i - m) * v_i
    знаменатель = dtype(0)                   # сумма exp(s_i - m)
    for i in range(0, len(s), блок):
        sb, vb = s[i:i + блок], V[i:i + блок]
        m_new = max(m, sb.max())
        k = np.exp(m - m_new)                # во сколько раз уменьшить накопленное
        w = np.exp(sb - m_new)
        числитель = числитель * k + w @ vb
        знаменатель = знаменатель * k + w.sum()
        m = m_new
    return числитель / знаменатель


ref = обычное(s, V)
print("оценки:", np.round(s, 1))
print("обычный softmax :", np.round(ref, 3))
print("по блокам       :", np.round(по_блокам(s, V), 3))
print("макс. расхождение:", f"{np.abs(ref - по_блокам(s, V)).max():.1e}")

# то же в float16: exp(11,5) около 98 700 уже не помещается (максимум 65 504)
big = np.array([2, 11.5, 12, 3, 5, 12.5, 1, 0], dtype=np.float16)
with np.errstate(all="ignore"):
    w = np.exp(big)
    print("exp в float16   :", w[:3], "...")
    print("наивно, float16 :", np.round((w / w.sum()) @ V[:, :2].astype(np.float16), 3))
print("по блокам, fp16 :", np.round(по_блокам(big, V[:, :2], dtype=np.float16), 3))
print("эталон, float64 :", np.round(обычное(big.astype(np.float64), V[:, :2]), 3))
