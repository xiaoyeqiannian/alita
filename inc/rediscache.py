#coding: utf-8

"""
# Configuration

Support flask config

REDIS = {
    'default': {
        'host': '127.0.0.1',
        'port': 6379,
        'db': 0,
        'timeout': 3600
    }
}

note:
werkzeug version>1.0.0, the cache model is extracted out to 
cachelib, but the latesd cachelib have bug

TODO: use cachelib instead of werkzeug.contrib.cache
"""

from werkzeug.contrib.cache import RedisCache

redis_list = {}

class RedisClient(RedisCache):

    def __init__(self, app, conf_key, key_prefix=''):
        conf = app.config['REDIS'][conf_key]
        super(RedisClient, self).__init__(
                host = conf['host'],
                port = conf['port'],
                db = conf.get('db', 0),
                password = conf.get('password', None),
                default_timeout = conf.get('timeout', 300),
                key_prefix = key_prefix and key_prefix+':' or '')

    def hash_hdel(self, key, field):
        self._client.hdel(self.key_prefix + key, field)

    def hash_hmset(self, key, mapping):
        self._client.hmset(self.key_prefix + key, mapping)

    def hash_hset(self, key, field, value):
        self._client.hset(self.key_prefix + key, field, value)

    def hash_hget(self, key, field):
        return self._client.hget(self.key_prefix + key, field)

    def hash_hgetall(self, key):
        return self._client.hgetall(self.key_prefix + key)

    def hexists(self, key, field):
        return self._client.hexists(self.key_prefix + key, field)

    def zrank(self, name, key):
        return self._client.zrank(name, self.key_prefix + key)

    def zrevrangebyscore(self,
                         name,
                         max,
                         min,
                         start=None,
                         num=None,
                         withscores=False,
                         score_cast_func=float):
        return self._client.zrevrangebyscore(
            name,
            max,
            min,
            start=start,
            num=num,
            withscores=withscores,
            score_cast_func=score_cast_func)

    def zrangebyscore(self,
                      name,
                      min,
                      max,
                      start=None,
                      num=None,
                      withscores=False,
                      score_cast_func=float):
        return self._client.zrangebyscore(
            name,
            min,
            max,
            start=start,
            num=num,
            withscores=withscores,
            score_cast_func=score_cast_func)

    def zrevrange(self, name, start, end, withscores=False, score_cast_func=float):
        return self._client.zrevrange(
            name, start, end, withscores=withscores, score_cast_func=score_cast_func)

    def zrange(self, name, start, end, desc=False, withscores=False, score_cast_func=float):
        return self._client.zrange(
            name, start, end, desc=False, withscores=withscores, score_cast_func=score_cast_func)

    def zrem(self, name, *values):
        return self._client.zrem(name, *values)

    def zadd(self, name, *args, **kwargs):
        return self._client.zadd(name, *args, **kwargs)

    def expire(self, name, time):
        return self._client.expire(name, time)

    def zcount(self, name, min, max):
        return self._client.zcount(name, min, max)
