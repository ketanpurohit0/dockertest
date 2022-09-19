import logging.config

from datetime import datetime

from pathlib import Path

 

#pip install structlog

import structlog

 

logging.config.fileConfig(Path(".", "logging.ini"), disable_existing_loggers=False)

from structlog.stdlib import LoggerFactory

 

structlog.configure(logger_factory=LoggerFactory(), processors = [structlog.processors.JSONRenderer()])

logger = structlog.getLogger('rotating')

 

logger.error("ERRORM", you="Me", her="Her", me="Ketan")

logger.info("INFOM", me="Ketan", you="Purohit", ts=str(datetime.now()))

 

def foo():

    logger.info("Hi from foo")

   

foo()