#!/usr/bin/env python3
"""Модель онбординга сервисов (Uber, 2014) из главы 16 на пакете lethain/systems.
Запуск: python3 -I ch16_onboarding_model.py
Сравнивает сценарии по двум числам на 50-м раунде:
  очередь = RequestedServices (заявки ждут), готово = ServerCapacityAllocated (сервис выдан)."""
from systems.parse import parse

HEAD = """HiringRate(10)
ProductEngineers(1000)
[PotentialHires] > ProductEngineers @ HiringRate
[PotentialServices] > RequestedServices(10) @ ProductEngineers / 10
"""


def spec(err_port=0.2, err_puppet=0.2, err_merge=0.2, cap=10, self_service=False):
    """err_* - доля ошибок на трёх шагах; cap - сколько заявок команда берёт в работу за раунд."""
    limit = "" if self_service else f", {cap}"
    return HEAD + f"""RequestedServices > InflightServices(0{limit}) @ Leak(1.0)
InflightServices > PortNameAssigned @ Leak(1.0)
PortNameAssigned > PuppetGenerated @ Leak({1 - err_port:g})
PortNameAssigned > RequestedServices @ Leak({err_port:g})
PuppetGenerated > PuppetConfigMerged @ Leak({1 - err_puppet:g})
PuppetGenerated > InflightServices @ Leak({err_puppet:g})
PuppetConfigMerged > ServerCapacityAllocated @ Leak({1 - err_merge:g})
PuppetConfigMerged > PuppetGenerated @ Leak({err_merge:g})
"""


def clean(text):
    """Убираем строки с вероятностью 0: Leak(0) пакет не принимает."""
    return "\n".join(l for l in text.splitlines() if "Leak(0)" not in l)


SCENARIOS = [
    ("1. Без ошибок, 10 заявок в раунд", spec(0, 0, 0)),
    ("2. Ошибки по 20%", spec()),
    ("3. Больше ошибок на порту: 50%", spec(err_port=0.5)),
    ("4. Больше ошибок в Puppet: 50%", spec(err_puppet=0.5)),
    ("5. Больше ошибок при слиянии: 50%", spec(err_merge=0.5)),
    ("6. Команда выросла в 5 раз (50 заявок)", spec(cap=50)),
    ("7. Self-service (без лимита)", spec(self_service=True)),
]

ROUNDS = 50
print(f"{'Сценарий':<42}{'очередь':>9}{'готово':>9}")
for name, text in SCENARIOS:
    model = parse(clean(text))
    last = model.run(rounds=ROUNDS)[-1]
    print(f"{name:<42}{last['RequestedServices']:>9}{last['ServerCapacityAllocated']:>9}")
