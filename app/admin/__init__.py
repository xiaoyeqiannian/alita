#coding: utf-8

import os
from flask import Blueprint
from inc import app, rediscache
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect, generate_csrf

rc = rediscache.RedisClient(app, conf_key = "default", key_prefix="V10")
site_folder = os.path.abspath(os.path.dirname(__file__))
# template_folder:Location of the template files to be added to the template lookup.
mod = Blueprint('admin',
                __name__,
                url_prefix='/admin',
                template_folder=os.path.join(site_folder, 'templates'),
                static_folder='static')

csrf = CSRFProtect(app)

# login config
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.init_app(app=app)
login_manager.login_view = "admin.login"
"""
@login_manager.user_loader
def load_user(user_id):
    from app.admin.models import Manager
    manager = Manager.get(user_id)
    return manager
"""
@app.after_request
def after_request(response):
    csrf_token = generate_csrf()
    response.headers["csrf_token"] = csrf_token
    response.set_cookie("csrf_token", csrf_token, expires=60 * 30)
    return response
