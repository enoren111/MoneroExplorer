# -*- coding: utf-8 -*-
import os
import logging
import logging.handlers
import os.path


def init_logger(logger_file, logger_level=logging.DEBUG):

    logger = logging.getLogger(logger_file)
    logger.setLevel(logger_level)

    file_handler = logging.handlers.RotatingFileHandler(filename=logger_file,
                                                        maxBytes=1024 * 1024 * 1024, backupCount=10)
    formatter = logging.Formatter('%(asctime)s \t%(created)f \t%(levelname)s line-%(lineno)d, %(funcName)s\t%(message)s')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logger_level)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.ERROR)

    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

    logger.debug("logger init done")
    return logger