#coding: utf-8

from inc import db
from inc.cached import cached
from flask_sqlalchemy import event
from app.api.models import Account
from . import rc, mc, logger


class FAccount(Account):
    __abstract__ = True

    @classmethod
    @cached('%s:%s' % (Account.__tablename__,'{_id}'), mc, 3600)
    def get(cls, _id):
        phone = rc.hash_hget("hash:%s:%s" % (cls.__tablename__, _id), 'phone')
        name = rc.get("str:%s:%s" % (cls.__tablename__, _id))
        mc_name = mc.get("str:%s:%s" % (cls.__tablename__, _id))
        logger.debug("%s,%s,%s" % (phone, name, mc_name))

        account = db.session.query(Account).filter(Account.id==_id).first()
        if not account:
            return None

        rc.hash_hset("hask:%s:%s" % (cls.__tablename__, _id), 'phone', account.phone)
        rc.set("str:%s:%s" % (cls.__tablename__, _id), 'phone')
        mc.set("str:%s:%s" % (cls.__tablename__, _id), 'mc phone')
        return account

    @classmethod
    def query(cls, **kwargs):
        q = db.session.query(Account)
        if kwargs.get('account_id'):
            q = q.filter(Account.id == kwargs.get('account_id'))
        if kwargs.get('phone'):
            q = q.filter(Account.phone == kwargs.get('phone'))
        if kwargs.get('nickname'):
            q = q.filter(Account.nickname == kwargs.get('nickname'))
        if kwargs.get('state'):
            q = q.filter(Account.state == kwargs.get('state'))
        page = kwargs.get('page', 1)
        per_page = kwargs.get('per_page', 10)
        pagination = q.order_by(Account.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
        next_page = pagination.next_num if pagination.has_next else page
        return pagination.items, pagination.total, next_page

    @classmethod
    def modify(cls, _id, **kwargs):
        #note: directly use update,cann't trigger ‘after_update’ event
        c = cls.get(_id)
        if not c:
            return False

        c.phone = kwargs.get('phone', c.phone)
        c.nickname = kwargs.get('nickname', c.nickname)
        c.password = kwargs.get('password', c.password)
        c.state = kwargs.get('state', c.state)
        db.session.add(c)
        db.session.commit()
        return True

    @classmethod
    def add(cls, **kwargs):
        account = Account(
                    phone = kwargs.get('phone', ''),
                    nickname = kwargs.get('nickname', ''),
                    state = 1
        )
        db.session.add(account)
        db.session.commit()

    @classmethod
    def delete(cls, _id):
        c = cls.get(_id)
        db.session.delete(c)
        db.session.commit()

    @event.listens_for(Account, "after_insert", propagate=False)
    def listen_add_account(self, connection, target):
        print("after_insert", target)

    @event.listens_for(Account, "after_update", propagate=False)
    def listen_update_account(self, connection, target):
        print("after_update", target)
        mc.delete('%s:%s' % (Account.__tablename__, target.id))

    @event.listens_for(Account, "before_delete", propagate=False)
    def listen_delete_account(self, connection, target):
        print("before_delete", target)
