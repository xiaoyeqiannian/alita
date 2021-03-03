import jwt
import logging
from functools import wraps
from datetime import datetime
from werkzeug.local import LocalProxy
from flask import request, jsonify, _request_ctx_stack, current_app, Response
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import HTTPException

from util.consts import *
from inc.retcode import RETCODE
from inc.casbin_adapter import rbac
from .exceptions import (ServerException, Success, DatabaseException,
                        UnderDevelopment, UnknownException, LoginError)


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
            raise LoginError(message = 'Require authorization!')

        parts = auth_header_value.split()
        if len(parts) == 1:
            raise LoginError(message = 'Require token!')

        elif len(parts) > 2:
            raise LoginError(message = 'Token invalid!')

        token = parts[1]
        if token is None:
            raise LoginError(message = 'Token error!')

        try:
            payload = jwt_decode(token)
        except jwt.InvalidTokenError as e:
            raise LoginError(message="Token invalid!")

        if payload.get('identity') is None:
            raise LoginError(message = "Identity is None!")

        _request_ctx_stack.top.current_identity = payload.get('identity')
        return fn(*args, **kwargs)
    return wapper


def verify_permission(func):
    @wraps(func)
    def wapper(*args, **kwargs):
        role_id = current_identity.get('role_id')
        role = role_id==ROLE_ROOT_ID and 'root' or str(role_id) # NOTE: root的role id是个固定值，需在系统初始时创建
        isok = rbac.enforce(role, request.path, str.lower(request.method))
        if isok:
            return func(*args, **kwargs)
        else:
            return jsonify(code=RETCODE.ROLEERR, msg="Permission error!")

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


def except_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            ret = func(*args, **kwargs) or {}

        except ServerException as e:
            return jsonify(e.to_dict())

        except SQLAlchemyError as e:
            return jsonify(DatabaseException(e).to_dict())

        except HTTPException as e:  # abort 404/405/...
            raise e

        except Exception as e:
            return jsonify(UnknownException(e).to_dict())

        else:
            if isinstance(ret, dict):
                return jsonify(Success(data=ret).to_dict())

            return ret

    return wrapper