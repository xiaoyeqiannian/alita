import jwt
import logging
from functools import wraps
from datetime import datetime
from werkzeug.local import LocalProxy
from flask import request, jsonify, _request_ctx_stack, current_app

from util.consts import *
from inc.retcode import RETCODE
from inc.casbin_adapter import rbac


current_identity = LocalProxy(lambda: getattr(_request_ctx_stack.top, 'current_identity', None))


def jwt_payload(identity):
    iat = datetime.utcnow()
    exp = iat + current_app.config.get('JWT_EXPIRATION_DELTA')
    return {'exp': exp, 'iat': iat, 'identity': identity }


def jwt_encode(identity):
    secret = current_app.config['JWT_SECRET_KEY']
    algorithm = current_app.config['JWT_ALGORITHM']
    required_claims = current_app.config['JWT_REQUIRED_CLAIMS']

    payload = jwt_payload(identity)
    missing_claims = list(set(required_claims) - set(payload.keys()))

    if missing_claims:
        raise RuntimeError('Payload is missing required claims: %s' % ', '.join(missing_claims))

    return jwt.encode(payload, secret, algorithm=algorithm, headers=None)


def jwt_decode(token):
    secret = current_app.config['JWT_SECRET_KEY']
    algorithm = current_app.config['JWT_ALGORITHM']
    leeway = current_app.config['JWT_LEEWAY']

    verify_claims = current_app.config['JWT_VERIFY_CLAIMS']
    required_claims = current_app.config['JWT_REQUIRED_CLAIMS']

    options = {
        'verify_' + claim: True
        for claim in verify_claims
    }

    options.update({
        'require_' + claim: True
        for claim in required_claims
    })

    return jwt.decode(token, secret, options=options, algorithms=[algorithm], leeway=leeway)


def jwt_required(fn):
    @wraps(fn)
    def wapper(*args, **kwargs):
        auth_header_value = request.headers.get('Authorization', None)
        if not auth_header_value:
            return jsonify(code=RETCODE.LOGINERR, msg='Authorization缺失')

        parts = auth_header_value.split()
        if len(parts) == 1:
            return jsonify(code=RETCODE.LOGINERR, msg='Token缺失')

        elif len(parts) > 2:
            return jsonify(code=RETCODE.LOGINERR, msg='Token无效')

        token = parts[1]
        if token is None:
            return jsonify(code=RETCODE.LOGINERR, msg='Token异常')

        try:
            payload = jwt_decode(token)
        except jwt.InvalidTokenError as e:
            return jsonify(code=RETCODE.LOGINERR, msg=str(e))

        _request_ctx_stack.top.current_identity = payload.get('identity')

        if payload.get('identity') is None:
            return jsonify(code=RETCODE.LOGINERR, msg='用户不存在')

        return fn(*args, **kwargs)
    return wapper


def verify_permission(func):
    @wraps(func)
    def wapper(*args, **kwargs):
        role_id = current_identity.get('role_id')
        user_id = current_identity.get('user_id')
        role = user_id==ROLE_ROOT_ID and 'root' or str(role_id) # NOTE: root的role id是个固定值，需在系统初始时创建
        isok = rbac.enforce(role, request.path, str.lower(request.method))
        if isok:
            return func(*args, **kwargs)
        else:
            return jsonify(code=RETCODE.ROLEERR, msg='您无此操作权限,请联系管理员!')

    return wapper


def log2file(func):
    '''保存输入输出日志'''
    @wraps(func)
    def wapper(*args, **kwargs):
        value = func(*args, **kwargs)
        if request.method == "GET":
            logger.info('%s|%s|%s|%s' % (func.__name__, request.args.to_dict(), request.form.to_dict(), value.data))
        else:
            logger.info('%s|%s|%s' % (func.__name__, request.json, value.data))

        return value
    return wapper