from flask import Blueprint
from inc import app, rediscache

rc = rediscache.RedisClient(app, conf_key = "default", key_prefix="APIV10")
mod = Blueprint('account', __name__, url_prefix='/account')