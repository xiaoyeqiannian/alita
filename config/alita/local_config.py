# the absolute log path
LOGPATH = "/home/luna/alita/log/"

################################################
DEBUG = True
TEMPLATE_DEBUG = True
EXPLAIN_TEMPLATE_LOADING = False
TEMPLATES_AUTO_RELOAD=True
#################################################

# DB
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
