#coding: utf-8

import operator
from decimal import Decimal

from sqlalchemy import inspect

def model2dict(row):

    temp_dict = {}

    for c in inspect(row).mapper.column_attrs:
        if not isinstance(getattr(row, c.key), (list, dict, int, Decimal, long)):
            temp_dict[c.key] = '' if not getattr(row, c.key) else getattr(row, c.key)
        else:
            temp_dict[c.key] = getattr(row, c.key)

    return ObjectDict(temp_dict)


class ObjectDict(dict):
    """
    Makes a dictionary behave like an object, with attribute-style access.
    """

    def __getattr__(self, name):
        try:

            if not isinstance(self[name], (list, dict, int, Decimal, long)):
                return "" if not self[name] else self[name]
            else:
                return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):

        if not isinstance(value, (list, dict, int, Decimal, long)):
            self[name] = "" if not value else value
        else:
            self[name] = value

    @staticmethod
    def create(args):
        assert isinstance(args, dict)
        d = ObjectDict(args)
        for k, v in d.iteritems():
            if isinstance(v, dict):
                d[k] = ObjectDict.create(v)
        return d


def sort(d, reverse=True):
    return sorted(d.items(), key=operator.itemgetter(1), reverse=reverse)
