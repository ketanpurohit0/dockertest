import os
import pathlib
from random import randint
import time

from celery import Celery
from poc_worker2 import split_other, split_pdf

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "sqla+sqlite:///celery_broker.sqlite")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "db+sqlite:///celery_result.sqlite")
celery.conf.task_routes = {'poc_worker1.process_pdf': {"queue": "stage1_Queue"}, "poc_worker1.process_other": {"queue": "stage1_Queue"}}  # noqa: E501


@celery.task
def process_pdf(path: str):
    # demo some acivity that takes some time
    _path = pathlib.Path(path)
    print(_path)
    jitter = randint(0, 3)
    time.sleep(len(_path.name)//2 + jitter)
    split_pdf.delay(path)

    return True


@celery.task
def process_other(path: str):
    # demo some acivity that takes some time
    _path = pathlib.Path(path)
    print(_path)
    time.sleep(len(_path.name)//2)
    split_other.delay(path)
    return True


# celery --app=poc_worker1.celery worker --loglevel=info --queues stage1_Queue

