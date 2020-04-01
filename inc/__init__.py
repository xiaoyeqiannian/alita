#coding: utf-8

import os
import sys
import importlib
import flask
import jinja2
from flask import Flask, g, url_for
from flask_sqlalchemy import SQLAlchemy

app = None
db = None
csrf = None


def install_models(app_names):
    '''先创建 models, 从每个应用的 models.py 里加载
    '''
    for name in app_names:
        try:
            models_name = "{}.models".format(name)
            mod = importlib.import_module(models_name)
            print("%s models imported" % models_name)
        except ImportError as e:
            if 'No module named models' not in str(e):
                print("%s (models) import failed: %r" % (models_name, e))
        except Exception as e:
            print("%s import failed: %r" % (models_name, e)) 


def install():
    """
    加载应用程序
    """
    global db, app, csrf

    def _import_custom_models(library_views):
        # 加载 xx/views.py
        try:
            mod_views = importlib.import_module(library_views)
            print("%s imported" % (library_views))

            # 每个 views.py 有个名为 mod 的 blueprint
            if hasattr(mod_views, 'mod'):
                app.register_blueprint(getattr(mod_views, 'mod'))
            # 或者名为 mod_user / mod_detail 等 blueprint 也可以
            else:
                for name, value in vars(mod_views).iteritems():
                    if name.startswith('mod_'):
                        app.register_blueprint(value)

        except ImportError as e:
            # 如果没有实现 .views, 静默处理即可
            if not 'No module named views' in str(e):
                print("%s install failed: %r" % (library_views, e))
        except Exception as e:
            print("%s install failed: %r" % (library_views, e))

    # 需要加载的app 从配置中获取
    app_names = app.config['INSTALLED_APPS']
    for name in app_names:
        print("install trying %s" % (name))
        library_views = "{}.views".format(name)
        _import_custom_models(library_views)

def per_request_callbacks(resp):
    for func in getattr(g, 'call_after_request', ()):
        resp = func(resp)
    return resp

_model_installed = False
def create_app(config=None):
    """
    创建应用程序初始化
    :param config:
    :return:
    """
    if False:
        import traceback
        traceback.print_stack()

    global app, db

    app = Flask(__name__)
    print("create app(%s) id:%s" % (__name__, id(app)))

    global FORMAT

    assert config
    # 加载config的路径
    relative_path = os.path.join('..', config)
    # 从python文件中更新配置的值
    x = app.config.from_pyfile(relative_path, silent=False)

    print("load config %s" % (relative_path))

    app.config['TEMPLATE_DEBUG'] = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True

    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True
    db = SQLAlchemy(app)
    print("create db id:%s via %r" % (id(db), SQLAlchemy))

    global _model_installed
    if not _model_installed:
        _model_installed = True
        install_models(app.config['INSTALLED_APPS'])

    assert db
    db.create_all()

    install()

    app.after_request(per_request_callbacks)
    return app
