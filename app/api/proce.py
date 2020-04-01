# coding: utf-8

import logging
from datetime import datetime
from app.api.fusion import FAccount
logger = logging.getLogger(__name__)

def get_accounts(**kwargs):
    accounts, total_count, next_page = FAccount.query(**kwargs)
    ret = []
    for c in accounts:
        ret.append({
            "account_id": c.id,
            "phone": c.phone,
            "nickname": c.nickname,
            "create_time": c.create_time and datetime.strftime(c.create_time, "%Y-%m-%d %H:%M:%S") or ''
            })
    return ret, total_count, next_page

def modify_account_info(_id, **kwargs):
    return FAccount.modify(_id, **kwargs)

def disable_account(_id):
    return FAccount.modify(_id, state=2)

def enable_account(_id):
    return FAccount.modify(_id, state=1)

def delete_account(_id):
    return FAccount.delete(_id)

def get_account(_id):
    c = FAccount.get(_id)
    if not c:
        return {}

    return {
            "account_id": c.id,
            "phone": c.phone,
            "nickname": c.nickname,
            "create_time": c.create_time and datetime.strftime(c.create_time, "%Y-%m-%d %H:%M:%S") or ''
            }

def add_account(**kwargs):
    return FAccount.add(**kwargs)
