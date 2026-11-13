"""Глава 7: DAG стартует от сообщения в Kafka (MessageQueueTrigger + AssetWatcher).
Для настоящего запуска нужен брокер Kafka. Здесь проверяется только разбор DAG."""
from airflow.providers.common.messaging.triggers.msg_queue import MessageQueueTrigger
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.sdk import DAG, Asset, AssetWatcher


def only_done(message):
    """Запускаем DAG только на сообщение «готово»."""
    return message.value() == b"done"


trigger = MessageQueueTrigger(
    scheme="kafka",
    topics=["uploads"],
    apply_function="ch07_kafka_dag.only_done",
    kafka_config_id="kafka_default",
)
uploads = Asset("uploads_topic", watchers=[AssetWatcher(name="uploads_watcher", trigger=trigger)])

with DAG(dag_id="ch07_on_upload", schedule=[uploads]):
    copy = EmptyOperator(task_id="copy_to_raw")
    process = EmptyOperator(task_id="process")
    copy >> process
