import os
import pathlib
from random import randint, choices
import time

from celery import Celery
from poc_worker2 import split_other, split_pdf
from celery.utils.log import get_task_logger

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "sqla+sqlite:///celery_broker.sqlite")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "db+sqlite:///celery_result.sqlite")
celery.conf.task_routes = {
    'poc_worker1.process_pdf'           : {"queue": "stage1_Queue"}, 
    "poc_worker1.process_other"         : {"queue": "stage1_Queue"},
    "poc_worker1.process_retry"         : {"queue": "stage1_Queue"},
    "poc_worker1.process_timelimited"   : {"queue": "stage1_Queue"},
    }  # noqa: E501
logger = get_task_logger(__name__)
logger.setLevel("DEBUG")

class RetryWhen(Exception):
    pass

@celery.task
def process_pdf(path: str):
    # demo some acivity that takes some time
    _path = pathlib.Path(path)
    print(_path)
    logger.info(_path)
    jitter = randint(0, 3)
    time.sleep(len(_path.name)//2 + jitter)
    split_pdf.delay(path)

    return True


@celery.task
def process_other(path: str):
    # demo some acivity that takes some time
    _path = pathlib.Path(path)
    print(_path)
    logger.debug(_path)
    time.sleep(len(_path.name)//2)
    split_other.delay(path)
    return True


@celery.task(autoretry_for = (RetryWhen,),
                max_retries = 5,
                retry_backoff = 3,
                retry_backoff_max = 24,
                retry_jitter = True)
def process_retry():
    # demo some acivity that takes some time and could timeout
    r = choices([True, False], cum_weights = (50, 100), k = 1)
    if r[0]:
        logger.error("We have an error")
        raise RetryWhen("Exception should result in retry")
    return True


@celery.task(time_limit = 5)
def process_timelimited():
    # demo some acivity that takes some time and could timeout
    r = choices([1, 3, 8], cum_weights = (30, 60, 100), k = 1)
    # There is a chance that this sleep will exceed the time_limit
    time.sleep(r[0])
    return True
# celery --app=poc_worker1.celery worker --loglevel=info --queues stage1_Queue

