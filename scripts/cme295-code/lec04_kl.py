"""KL в двух направлениях и сигнал по токенам в on-policy distillation."""
import numpy as np


def kl(p, q):
    """KL(p || q): мир задаёт p, насколько плохо описывать его через q."""
    p, q = np.array(p), np.array(q)
    return float(np.sum(p * np.log(p / q)))


# Часть 1. Учитель с двумя пиками (токены 0 и 4). Ученик слабее: пик у него один или нет вовсе.
teacher = [0.45, 0.05, 0.05, 0.05, 0.40]
student_mode = [0.90, 0.025, 0.025, 0.025, 0.025]             # ученик выбрал один пик
student_flat = [0.20, 0.20, 0.20, 0.20, 0.20]                 # ученик размазал вероятность
print("ученик          KL(учитель||ученик)  KL(ученик||учитель)")
for name, s in [("один пик", student_mode), ("размазан", student_flat)]:
    print(f"{name:14s}  прямая {kl(teacher, s):6.3f}       обратная {kl(s, teacher):6.3f}")

# Часть 2. Сигнал по токенам: ученик написал «Teddy climbs out of the box».
# Для каждого токена: вероятность у ученика и у учителя при одном и том же контексте.
tokens = ["Teddy", "climbs", "out", "of", "the box"]
p_student = np.array([0.50, 0.30, 0.70, 0.90, 0.80])
p_teacher = np.array([0.60, 0.02, 0.50, 0.90, 0.85])
penalty = np.log(p_student / p_teacher)                       # оценка обратной KL по одному токену
print("\nтокен       ученик  учитель  штраф log(s/t)")
for t, s, u, c in zip(tokens, p_student, p_teacher, penalty):
    print(f"{t:10s}  {s:.2f}    {u:.2f}    {c:6.2f}")
print("GRPO дал бы всем пяти токенам один и тот же сигнал: общий итог ответа")
