#coding: utf-8
import json

import datetime
from decimal import Decimal

import flask
from flask import jsonify


class JSONEncoder(json.JSONEncoder):
    '''能输出 datetime'''

    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(o, datetime.date):
            return o.strftime("%Y-%m-%d")
        if isinstance(o, Decimal):
            return str(Decimal(o).quantize(Decimal('0.00')))

        return super(JSONEncoder, self).default(o)

def object2dict(obj):
    #convert object to a dict
    #d = object2dict(p)
    #print(d)
    #{'age': 22, '__module__': 'Person', '__class__': 'Person', 'name': 'Peter'}
    d = {}
    d['__class__'] = obj.__class__.__name__
    d['__module__'] = obj.__module__
    d.update(obj.__dict__)
    return d

def dict2object(d):
    #convert dict to object
    if'__class__' in d:
        class_name = d.pop('__class__')
        module_name = d.pop('__module__')
        module = __import__(module_name)
        class_ = getattr(module,class_name)
        args = dict((key.encode('ascii'), value) for key, value in d.items()) #get args
        inst = class_(**args) #create new instance
    else:
        inst = d
    return inst

def queryset2json(ret):
    data = {}
    for k, v in ret:
        try:
            data[k] = json.loads(v)
        except:
            data[k] = v
    return data

def dumps(d):
    # TODO: with ensure_ascii=False, dart convert failed
    return json.dumps(d, cls=JSONEncoder, ensure_ascii=False)
    # return json.dumps(d, cls=JSONEncoder)

def build_json_data(data={}, result_code=0, msg=''):
    result = {"code": result_code,
              "msg": msg,
              "data": data
              }
    return result

def build_json_data_flag(data={}, result_code=0, msg='', info_id=0):
    result = {"code": result_code,
              "msg": msg,
              "info_id": info_id,
              "data": data
              }
    return result

def jsonify_data(data={}, result_code=0, status_code = 200, msg="", cache_control= 300):
    return jsonify(build_json_data(data, result_code, msg)), status_code, {'Content-Type': 'application/json', 'Cache-Control': cache_control}

def jsonify_response(data={}, result_code=0, status_code = 200, msg="", cache_control= 300):

    body = build_json_data(data, result_code, msg)

    resp = flask.make_response(dumps(body))

    resp.headers["Content-Type"] = 'application/json;charset=utf-8'

    if cache_control:
        resp.cache_control.max_age = cache_control

    # TODO: 添加更多 http header
    return resp

def json_dumps(data={}, result_code=0, status_code = 200, msg="", cache_control= 300):
    return json.dumps(build_json_data(data, result_code, msg)), status_code, {'Content-Type': 'application/json', 'Cache-Control': cache_control}

def json_dumps_flag(data={}, result_code=0, status_code = 200, msg="", cache_control=300, info_id=0):
    return json.dumps(build_json_data_flag(data, result_code, msg, info_id)), status_code, {'Content-Type': 'application/json', 'Cache-Control': cache_control}

def json_dumps_not_format(data={}, status_code = 200, cache_control= 300):
    return json.dumps(data), status_code, {'Content-Type': 'application/json', 'Cache-Control': cache_control}
