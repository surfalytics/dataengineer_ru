"""Конверсия филиала: покупки / посетители, в процентах.
Запуск: python3 scripts/conversion.py <покупки> <посетители>"""
import sys


def conversion(units: float, footfall: float) -> str:
    if footfall == 0:  # посетителей не было: делить нельзя
        return "0.0%"
    return f"{units / footfall * 100:.1f}%"


if __name__ == "__main__":
    print(conversion(float(sys.argv[1]), float(sys.argv[2])))
