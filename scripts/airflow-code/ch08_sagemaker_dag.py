"""Глава 8: DAG обучения модели в SageMaker (сокращённая версия). Только описание, в AWS не ходит.
Имя training job содержит logical_date, wait_for_completion=True ждёт конца job."""
import pendulum
from airflow.providers.amazon.aws.operators.s3 import S3CopyObjectOperator
from airflow.providers.amazon.aws.operators.sagemaker import SageMakerTrainingOperator
from airflow.sdk import DAG

BUCKET = "my-mnist-bucket"

with DAG(
    dag_id="mnist_train",
    schedule=None,
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
):
    copy_data = S3CopyObjectOperator(
        task_id="download_mnist_data",
        source_bucket_name="sagemaker-sample-data-eu-west-1",
        source_bucket_key="algorithms/kmeans/mnist/mnist.pkl.gz",
        dest_bucket_name=BUCKET,
        dest_bucket_key="mnist.pkl.gz",
    )
    train = SageMakerTrainingOperator(
        task_id="sagemaker_train_model",
        config={
            "TrainingJobName": "mnistclassifier-{{ logical_date | ts_nodash }}",
            # ... остальной config: образ, гиперпараметры, S3-пути, роль ...
        },
        wait_for_completion=True,  # task успешна, только когда job в AWS закончилась
        print_log=True,
        check_interval=10,  # опрос AWS каждые 10 секунд
    )
    copy_data >> train
