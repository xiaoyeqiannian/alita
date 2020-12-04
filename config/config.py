import os
import sys
from datetime import timedelta
HOME = os.path.dirname(os.path.abspath(__file__))
sys.path.append(HOME)

# the apps for loading
INSTALLED_APPS = [
    'app.account',
]

# the absolute log path
LOGPATH = ""

################################################
DEBUG = True
#################################################

# Flask-Security features
# SECURITY_REGISTERABLE = False
# SECURITY_SEND_REGISTER_EMAIL = False

# JWT CONFIG
JWT_SECRET_KEY = "alita666666"
JWT_EXPIRATION_DELTA = timedelta(seconds=3600*48)
JWT_VERIFY_CLAIMS = ['signature', 'exp', 'iat']
JWT_REQUIRED_CLAIMS = ['exp', 'iat']
JWT_AUTH_ENDPOINT = 'jwt'
JWT_ALGORITHM = 'HS256'
JWT_LEEWAY = timedelta(seconds=10)
JWT_AUTH_HEADER_PREFIX = 'JWT'
JWT_NOT_BEFORE_DELTA = timedelta(seconds=0)

# casbin 权限模块的配置目录，相对于inc的casbin_adapter
CASBIN_CONFIG_PATH = './config/rbac_model.conf'

# DB
SQLALCHEMY_ECHO = False
SQLALCHEMY_POOL_SIZE = 60
SQLALCHEMY_POOL_TIMEOUT = 30
SQLALCHEMY_MAX_OVERFLOW = 10
SQLALCHEMY_POOL_RECYCLE = 15
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = 'mysql://user:password@127.0.0.1:3306/alita?charset=utf8mb4'
# SQLALCHEMY_BINDS = {
#     'alita_admin': 'mysql://user:password@127.0.0.1:3306/alita_admin?charset=utf8',
# }

# 雪花算法参数
DATACENTER_ID = 0 #数据中心（机器区域）ID
WORKER_ID = 0 #机器ID

# CACHE
MEMCACHES = {
    'default': {
        'servers': ('127.0.0.1:11211', ),
        'behaviors': {
            'verify_keys': True,
            'tcp_nodelay': True,
            'hash': 'murmur',
            'distribution': 'consistent',
            'retry_timeout': 1,
            'buffer_requests': False,
            'dead_timeout': 60,
            'remove_failed': True,
            'no_block': True,
        }
    },
}

REDIS = {
    'default': {
        'host': '127.0.0.1',
        'port': 6379,
        'db': 0,
        'timeout': 3600
    },
}

# Email config
MAIL_HOST=""  #设置服务器
MAIL_USER=""    #用户名
MAIL_PWD=""   #口令 
MAIL_PORT = 25

try:
    # load local config instead of this config file
    from local_config import *
except ImportError:
    pass
