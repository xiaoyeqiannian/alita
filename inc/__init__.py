#coding: utf-8

import os
import sys
import importlib
import jinja2
from flask import Flask, g
from flask_sqlalchemy import SQLAlchemy


app = None
db = None


def install_models(app_names):
    '''
    create models from app's models.py
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
    load application
    """
    global db, app

    def _import_custom_models(library_views):
        # load xx/views.py
        try:
            mod_views = importlib.import_module(library_views)
            print("%s imported" % (library_views))

            # every views.py have a blueprint named mod
            if hasattr(mod_views, 'mod'):
                app.register_blueprint(getattr(mod_views, 'mod'))
            # or named mod_user / mod_detail maybe bester
            else:
                for name, value in vars(mod_views).iteritems():
                    if name.startswith('mod_'):
                        app.register_blueprint(value)

        except ImportError as e:
            # if haven't .views, Silent processing with except
            if not 'No module named views' in str(e):
                print("%s install failed: %r" % (library_views, e))
        except Exception as e:
            print("%s install failed: %r" % (library_views, e))

    # load apps from config
    app_names = app.config['INSTALLED_APPS']
    for name in app_names:
        print("install trying %s" % (name))
        library_views = "{}.views".format(name)
        _import_custom_models(library_views)


def per_request_callbacks(resp):
    for func in getattr(g, 'call_after_request', ()):
        resp = func(resp)
    return resp


def create_app(config=None):
    """
    initialize application
    """
    if False:
        import traceback
        traceback.print_stack()

    global app, db

    app = Flask(__name__)
    print("create app(%s) id:%s" % (__name__, id(app)))

    assert config
    # load config path
    relative_path = os.path.join('..', config)
    # update config from python file
    x = app.config.from_pyfile(relative_path, silent=False)

    print("load config %s" % (relative_path))

    app.config['TEMPLATE_DEBUG'] = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    db = SQLAlchemy(app)
    print("create db id:%s via %r" % (id(db), SQLAlchemy))

    install_models(app.config['INSTALLED_APPS'])

    assert db
    db.create_all()

    install()

    app.after_request(per_request_callbacks)
    return app
