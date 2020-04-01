#coding: utf-8

from flask import Blueprint
from inc import app, rediscache, memcached, logger

rc = rediscache.RedisClient(app, conf_key = "default", key_prefix="APIV10")
mc = memcached.MemcacheClient(app, conf_key = "default", key_prefix="APIV10")
logger = logger.applogger(__name__, app.config['LOGPATH'])
mod = Blueprint('api',
                __name__,
                url_prefix='/api')
