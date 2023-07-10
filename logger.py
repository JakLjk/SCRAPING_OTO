import logging 
from config import Config


if Config.LoggingSetup.LOG_FILE_PATH_NAME:
        handlers = [logging.FileHandler(Config.LOG_FILE_PATH_NAME),
                    logging.StreamHandler()]
else: 
    handlers = [logging.StreamHandler()]

logger = logging
logger.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s ||| [%(threadName)s] ",
    handlers=handlers)