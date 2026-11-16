"""Глава 9: lease, пауза процесса и fencing token.

Время здесь модельное (секунды-числа), поэтому запуск всегда даёт один и тот же вывод.
Запуск: python3 -I scripts/ddia-code/ch09_lease_pause.py
"""


class LockService:
    """Выдаёт lease на ttl секунд. Каждый новый lease получает token на 1 больше."""

    def __init__(self, ttl):
        self.ttl, self.token, self.holder, self.expires = ttl, 32, None, 0

    def acquire(self, client, now):
        if self.holder and now < self.expires:
            return None  # lease ещё у другого клиента
        self.token += 1
        self.holder, self.expires = client, now + self.ttl
        return self.token, self.expires


class Storage:
    """Хранилище файла. С fencing=True помнит самый большой token и отклоняет меньшие."""

    def __init__(self, fencing):
        self.fencing, self.max_token, self.log = fencing, 0, []

    def write(self, client, token, data):
        if self.fencing and token < self.max_token:
            return f"отклонено (token {token} < {self.max_token})"
        self.max_token = max(self.max_token, token)
        self.log.append(f"{client}:{data}")
        return "принято"


def scenario(fencing):
    print(f"--- хранилище {'с проверкой' if fencing else 'без проверки'} fencing token ---")
    locks, store = LockService(ttl=30), Storage(fencing)
    t1, exp1 = locks.acquire("client1", now=0)
    print(f"t=0   client1 получил lease, token {t1}, lease до t={exp1}")
    print(f"t=5   client1 проверил lease: в запасе {exp1 - 5} с, можно писать")
    # здесь client1 замирает: пауза GC на 40 секунд
    t2, _ = locks.acquire("client2", now=31)
    print(f"t=31  lease client1 истёк, client2 получил lease, token {t2}")
    print(f"t=32  client2 пишет: {store.write('client2', t2, 'B')}")
    print(f"t=45  client1 проснулся и пишет: {store.write('client1', t1, 'A')}")
    print(f"      в хранилище: {store.log}")


if __name__ == "__main__":
    scenario(fencing=False)
    scenario(fencing=True)
