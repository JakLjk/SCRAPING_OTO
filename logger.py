import logging 
from logging.handlers import RotatingFileHandler
from pathlib import Path

from config import Config

config_path = Config.LoggingSetup.RELATIVE_LOG_FILE_PATH_NAME
max_mbyte_size = Config.LoggingSetup.MAX_MB_SIZE_OF_CONFIG
log_backup_count = Config.LoggingSetup.LOG_BACKUP_FILES

log_format = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s ||| [%(threadName)s] ")

if config_path:    
        base_path = str(Path(__file__).parent)
        full_path = base_path + config_path

        file_handler = RotatingFileHandler(full_path,
                                           mode='a',
                                           maxBytes=max_mbyte_size*1024*1024,
                                           backupCount=log_backup_count,
                                           encoding=None,
                                           delay=0)
        file_handler.setFormatter(log_format)
        file_handler.setLevel(logging.INFO)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(log_format)
        stream_handler.setLevel(logging.INFO)

        logger = logging.getLogger('root')
        logger.setLevel(logging.INFO)
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

else: 
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(log_format)
    stream_handler.setLevel(logging.INFO)
    logger = logging.getLogger('root')
    logger.setLevel(logging.INFO)
    logger.addHandler(stream_handler)
