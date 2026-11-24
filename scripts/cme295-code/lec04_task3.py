"""Задача 3: KL в двух направлениях."""
import math


def kl(p, q):
    return sum(pi * math.log(pi / qi) for pi, qi in zip(p, q))


teacher = [0.7, 0.2, 0.1]
student = [0.3, 0.3, 0.4]
print(f"KL(teacher||student) = {kl(teacher, student):.3f}")
print(f"KL(student||teacher) = {kl(student, teacher):.3f}")
