#coding: utf-8

"""
# Configuration

Support flask config

CACHES = {
    'GROUP1': {
        'servers': ('localhost:11211:3', 'localhost:11212',),
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
            'remove_failed': True
        }
    }
}

> behaviors document
> http://sendapatch.se/projects/pylibmc/behaviors.html

TODO: use cachelib instead of werkzeug.contrib.cache

"""
import json
from werkzeug.contrib.cache import MemcachedCache
from util.object_dict import ObjectDict


class MemcacheClient(MemcachedCache):
    '''add behaviors
    compatible with pylibmc'''

    def __init__(self, app, conf_key='default', key_prefix=''):
        if conf_key not in app.config['MEMCACHES']:
            return

        conf = app.config['MEMCACHES'][conf_key]
        assert isinstance(conf, dict)

        super(MemcacheClient, self).__init__(
                                servers=conf['servers'],
                                key_prefix=key_prefix and key_prefix+':' or '')
        if 'behaviors' in conf:
            self._client.behaviors = conf['behaviors']

    def get_many(self, keys):
        '''pylibmc 返回的是 dict, werkzeug 返回的是 list'''
        ret = super(MemcacheClient, self).get_many(*keys)
        assert isinstance(ret, list)
        return dict(zip(keys, ret))

    def incr(self, key, val):
        return self._client.incr(key, val)

    def cas(self, key, val, cas):
        return self._client.cas(key, val, cas)

    def append(self, key, val):
        return self._client.append(key, val)

    def disconnect_all(self):
        self._client.close()

    def dict_set(self, key, od, timeout=None):
        assert isinstance(od, dict)
        return self.set(key, json.dumps(od), timeout=timeout)

    def dict_get(self, key):
        ods = self.get(key)
        if ods:
            return ObjectDict(json.loads(ods))
