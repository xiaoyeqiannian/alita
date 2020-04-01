# -*- coding:utf-8 -*-

import os
import logging
import logging.handlers
from inc.lazycreator import LazyCreator

_loggers = {}

def applogger(name, path, debug=False):
    if name not in _loggers:
        logger = LazyCreator(_create_applogger, path, name+'.log')
        _loggers[name] = logger

    return _loggers[name]


def _create_applogger(path, name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    for handler in logger.handlers:
        logger.removeHandler(handler)

    logfile = os.path.join(path, name)
    handler = logging.handlers.WatchedFileHandler(logfile, delay=True)
    handler.setFormatter(logging.Formatter('%(asctime)s %(process)d %(levelname)s %(message)s'))
    handler.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.propagate = False
    return logger
