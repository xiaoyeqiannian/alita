# coding: utf-8

from flask import request
from functools import wraps
from werkzeug.exceptions import Unauthorized
from flask_login import current_user, login_required
from app.admin.fusion import FManager 

def verify_permission(func):
    @login_required
    @wraps(func)
    def wapper(*args, **kwargs):
        user_obj = current_user
        if not (user_obj.is_active and user_obj.is_authenticated and hasattr(user_obj, "id")):
            raise Unauthorized

        if not user_obj.role_id:
            raise Unauthorized
            
        role = user_obj.role
        if not role:
            raise Unauthorized
            
        routes = role.routes and role.routes.split(',') or []
        current_user.routes = routes
        permission_ids = [p.id for p in role.permissions]
        role_en = role.en_name
        req_permission_id = func.__code__.co_consts[1]
        if "superadmin" == role_en  \
            or not req_permission_id \
            or int(req_permission_id) in permission_ids:  
            return func(*args, **kwargs)

        raise Unauthorized

    return wapper
