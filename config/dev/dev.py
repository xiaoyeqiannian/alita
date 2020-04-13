#coding: utf-8

# the apps for loading
INSTALLED_APPS = [
    'app.api',
    'app.admin',
]

# the absolute log path
LOGPATH = "/home/luna/alita/log/"

################################################
DEBUG = True
TEMPLATE_DEBUG = True
EXPLAIN_TEMPLATE_LOADING = False
#
# ################################################

# Flask-Security features
SECURITY_REGISTERABLE = False
SECURITY_SEND_REGISTER_EMAIL = False

# SESSION
SESSION_COOKIE_NAME = '_sa'

# login
SECRET_KEY = "alita666666"

# WTF
WTF_CSRF_FIELD_NAME = "csrf_token"
WTF_CSRF_HEADERS = ['X-CSRF-Token']
WTF_CSRF_CHECK_DEFAULT = False 

# DB
SQLALCHEMY_ECHO = False
SQLALCHEMY_POOL_SIZE = 60
SQLALCHEMY_POOL_TIMEOUT = 30
SQLALCHEMY_MAX_OVERFLOW = 10
SQLALCHEMY_POOL_RECYCLE = 15
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = 'mysql://alita:Alita@123@127.0.0.1:3306/alita?charset=utf8mb4'
SQLALCHEMY_BINDS = {
    'alita_admin': 'mysql://alita:Alita@123@127.0.0.1:3306/alita_admin?charset=utf8',
}

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
