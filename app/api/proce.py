import logging
from inc import db
from datetime import datetime
from inc.cached import cached
from flask_sqlalchemy import event
from app.api.models import Account
from . import rc, mc, logger

logger = logging.getLogger(__name__)


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


@cached('%s:%s' % (Account.__tablename__,'{_id}'), mc, 3600)
def get_account_by_id(_id):
    account = db.session.query(Account).filter(Account.id==_id).first()
    if not account:
        return None

    return account


def get_accounts(**kwargs):
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
    
    ret = []
    for c in pagination.items:
        ret.append({
            "account_id": c.id,
            "phone": c.phone,
            "nickname": c.nickname,
            "create_time": c.create_time and datetime.strftime(c.create_time, "%Y-%m-%d %H:%M:%S") or ''
            })
    return ret, pagination.total, next_page


def modify_account_info(_id, **kwargs):
    #note: directly use update,cann't trigger ‘after_update’ event
    c = get_account_by_id(_id)
    if not c:
        return False

    c.phone = kwargs.get('phone', c.phone)
    c.nickname = kwargs.get('nickname', c.nickname)
    c.password = kwargs.get('password', c.password)
    c.state = kwargs.get('state', c.state)
    db.session.add(c)
    db.session.commit()
    return True


def disable_account(_id):
    return modify_account_info(_id, state=2)


def enable_account(_id):
    return modify_account_info(_id, state=1)


def delete_account(_id):
    c = get_account_by_id(_id)
    db.session.delete(c)
    db.session.commit()


def get_account_jsonify(_id):
    c = get_account_by_id(_id)
    if not c:
        return {}

    return {
            "account_id": c.id,
            "phone": c.phone,
            "nickname": c.nickname,
            "create_time": c.create_time and datetime.strftime(c.create_time, "%Y-%m-%d %H:%M:%S") or ''
            }


def add_account(**kwargs):
    account = Account(
                phone = kwargs.get('phone', ''),
                nickname = kwargs.get('nickname', ''),
                state = 1
    )
    db.session.add(account)
    db.session.commit()
