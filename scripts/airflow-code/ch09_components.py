"""Глава 9: свои hook, operator, sensor и deferrable sensor вокруг выдуманного API заказов.
API отдаёт заказы страницами: параметры day, offset, limit. Ответ: {"items": [...], "total": N}.
Сетевой вызов только в hook. Проверка без сервера: ch09_check.py."""
import asyncio
import json
import os

import requests
from airflow.sdk import BaseHook, BaseOperator, BaseSensorOperator
from airflow.triggers.base import BaseTrigger, TriggerEvent


class OrdersHook(BaseHook):
    """Вся работа с API здесь. Адрес и пароль берём из Airflow Connection по conn_id."""

    def __init__(self, conn_id):
        super().__init__()
        self._conn_id = conn_id
        self._session = None  # кэш: не ходим в metastore при каждом вызове
        self._base_url = None

    def _connect(self):
        if self._session is None:
            conf = self.get_connection(self._conn_id)
            self._base_url = f"https://{conf.host}"
            self._session = requests.Session()
            if conf.login:
                self._session.auth = (conf.login, conf.password)
        return self._session, self._base_url

    def get_orders(self, day, batch_size=100):
        """Генератор заказов за день. Страницы читает лениво."""
        session, base = self._connect()
        offset, total = 0, None
        while total is None or offset < total:
            resp = session.get(
                f"{base}/orders",
                params={"day": day, "offset": offset, "limit": batch_size},
            )
            resp.raise_for_status()
            page = resp.json()
            yield from page["items"]
            offset += batch_size
            total = page["total"]

    def has_orders(self, day):
        """Есть ли хотя бы один заказ. Читаем одну запись."""
        return next(self.get_orders(day, batch_size=1), None) is not None

    def close(self):
        if self._session is not None:
            self._session.close()
            self._session = None


class OrdersFetchOperator(BaseOperator):
    """Забирает заказы за день и пишет их в JSON."""

    template_fields = ("day", "output_path")  # в этих полях работает Jinja

    def __init__(self, conn_id, output_path, day="{{ ds }}", **kwargs):
        super().__init__(**kwargs)  # retries, retry_delay и другие общие аргументы
        self.conn_id, self.output_path, self.day = conn_id, output_path, day

    def execute(self, context):
        hook = OrdersHook(self.conn_id)
        try:
            orders = list(hook.get_orders(self.day))
        finally:
            hook.close()  # закрываем, даже если запрос упал
        self.log.info("Fetched %s orders for %s", len(orders), self.day)
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        with open(self.output_path, "w") as f:
            json.dump(orders, f)
        return len(orders)


class OrdersSensor(BaseSensorOperator):
    """Ждёт, пока в API появится хотя бы один заказ за день."""

    template_fields = ("day",)

    def __init__(self, conn_id, day="{{ ds }}", **kwargs):
        super().__init__(**kwargs)
        self.conn_id, self.day = conn_id, day

    def poke(self, context):
        hook = OrdersHook(self.conn_id)
        try:
            return hook.has_orders(self.day)  # True: sensor завершён, False: ждём
        finally:
            hook.close()


class OrdersTrigger(BaseTrigger):
    """Живёт в процессе triggerer. Ждёт асинхронно и отдаёт TriggerEvent."""

    def __init__(self, conn_id, day, pause=30):
        super().__init__()
        self.conn_id, self.day, self.pause = conn_id, day, pause

    def serialize(self):
        # путь к классу и аргументы: по ним Airflow пересоздаёт trigger
        return (
            "ch09_components.OrdersTrigger",
            {"conn_id": self.conn_id, "day": self.day, "pause": self.pause},
        )

    async def run(self):
        found = False  # в книге здесь стоит True: цикл не работал бы
        while not found:
            found = await self._has_orders()
            if not found:
                await asyncio.sleep(self.pause)  # здесь worker не занят
        yield TriggerEvent({"day": self.day})

    async def _has_orders(self):
        # Клиент requests синхронный. Выносим вызов в поток, чтобы не блокировать triggerer.
        hook = OrdersHook(self.conn_id)
        try:
            return await asyncio.to_thread(hook.has_orders, self.day)
        finally:
            hook.close()


class OrdersSensorAsync(BaseOperator):
    """Deferrable sensor: отдаёт ожидание triggerer и освобождает worker slot."""

    template_fields = ("day",)

    def __init__(self, conn_id, day="{{ ds }}", pause=30, **kwargs):
        super().__init__(**kwargs)
        self.conn_id, self.day, self.pause = conn_id, day, pause

    def execute(self, context):
        self.defer(
            trigger=OrdersTrigger(self.conn_id, self.day, self.pause),
            method_name="execute_complete",
        )

    def execute_complete(self, context, event):
        self.log.info("Orders are ready for %s", event["day"])
