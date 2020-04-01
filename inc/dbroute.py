#coding: utf-8

import logging
from flask_sqlalchemy import SQLAlchemy as SQLAlchemyBase
from flask_sqlalchemy import get_state

import sqlalchemy.orm as orm
from functools import partial

logger = logging.getLogger(__name__)


def instance_get(cls, key, default=None):
    """
    fetch class instance attribute
    """
    return vars(cls).get(key, default)


class RoutingSession(orm.Session):
    _name = None

    def __init__(self, db, autocommit=False, autoflush=False, **options):
        self.db = db
        self.app = db.get_app()
        self._model_changes = {}
        orm.Session.__init__(self,
                             autocommit=autocommit,
                             autoflush=autoflush,
                             bind=db.engine,
                             binds=db.get_binds(self.app),
                             **options)

    def get_bind(self, mapper=None, clause=None):
        try:
            state = get_state(self.app)
        except (AssertionError, AttributeError, TypeError) as err:
            logger.error("Unable to get Flask-SQLAlchemy configuration."
                                  " Outputting default bind. Error:" + err)
            return orm.Session.get_bind(self, mapper, clause)

        bind_key = None
        slave = False

        if state is None or not self.app.config['SQLALCHEMY_BINDS']:
            logger.error("Connecting -> DEFAULT. Unable to get Flask-SQLAlchemy"
                                  " bind configuration. Outputting default bind.")
            return orm.Session.get_bind(self, mapper, clause)

        elif self._name:
            bind_key = self._name

        elif self._flushing:    # we who are about to write, salute you
            bind_key = instance_get(mapper.class_, '__bind_key__')
            logger.debug('use master: %s', bind_key)

        else:
            slave = True
            master_key = instance_get(mapper.class_, '__bind_key__')
            bind_key = "slave_{0}".format(master_key)
            print 'use slave: %s', bind_key
            logger.debug('use slave: %s', bind_key)

        try:
            x = state.db.get_engine(self.app, bind=bind_key)
        except:
            logger.debug('slave: %s not configure', bind_key)
            if slave:
                x = state.db.get_engine(self.app, bind=master_key)

        return x

    def using_bind(self, name):
        logger.debug("use_bind: %s", name)
        s = RoutingSession(self.db)
        vars(s).update(vars(self))
        s._name = name
        return s


class SQLAlchemy(SQLAlchemyBase):
    def __init__(self, *args, **kwargs):
        SQLAlchemyBase.__init__(self, *args, **kwargs)
        self.session.using_bind = lambda s: self.session().using_bind(s)

    def create_scoped_session(self, options=None):
        if options is None:
            options = {}
        scopefunc = options.pop('scopefunc', None)
        return orm.scoped_session(partial(RoutingSession, self, **options), scopefunc=scopefunc)


db = SQLAlchemy(session_options={'autocommit': True})

