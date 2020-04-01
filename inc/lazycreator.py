# -*- coding:utf-8 -*-

class LazyCreator(object):

    def __init__(self, factory, *a, **kw):
        def creator():
            return factory(*a, **kw)
        self.creator = creator
        self.__obj = None

    def __getattr__(self, attr):
        if self.__obj is None:
            self.__obj = self.creator()
        return getattr(self.__obj, attr)

