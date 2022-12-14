import os
import pathlib
from random import randint
import time

from celery import Celery


celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "sqla+sqlite:///celery_broker.sqlite")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "db+sqlite:///celery_result.sqlite")
celery.conf.task_routes = {'poc_worker2.split_pdf': {"queue": "stage2_Queue"}, "poc_worker2.split_other": {"queue": "stage2_Queue"}}  # noqa: E501


@celery.task
def split_pdf(path: str):
    # demo some acivity that takes some time
    _path = pathlib.Path(path)
    print(_path)
    jitter = randint(0, 3)
    time.sleep(len(_path.name)//2 + jitter)
    return True


@celery.task
def split_other(path: str):
    # demo some acivity that takes some time
    _path = pathlib.Path(path)
    print(_path)
    time.sleep(len(_path.name)//2)
    return True


# celery --app=poc_worker2.celery worker --loglevel=info --queues stage2_Queue
