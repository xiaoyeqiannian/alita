#coding: utf-8

import logging
from datetime import datetime
from inc import db
from app.admin.models import * 
from sqlalchemy import or_

logger = logging.getLogger(__name__)

class FManager(Manager):
    __abstract__ = True

    @property
    def state_cn(self):
        return ('待审核', '已审核', '已删除')[self.state]

    @classmethod
    def get(cls, _id):
        return db.session.query(Manager).filter(Manager.id==_id).first()

    @classmethod
    def get_by_phone(cls, phone):
        return db.session.query(Manager).filter(Manager.phone==phone).first()

    @classmethod
    def query(cls, page, per_page, **kwargs):
        q = db.session.query(Manager)# TODO filter superadmin
        if kwargs.get('manager_id'):
            q = q.filter(Manager.id == kwargs.get('manager_id'))
        if kwargs.get('phone'):
            q = q.filter(Manager.phone == kwargs.get('phone'))
        if kwargs.get('name'):
            q = q.filter(Manager.name == kwargs.get('name'))
        if kwargs.get('state'):
            q = q.filter(Manager.state == kwargs.get('state'))

        pagination = q.order_by(Manager.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
        return pagination

    @classmethod
    def modify(cls, _id, **kwargs):
        c = cls.get(_id)
        if not c:
            return False, '未找到此用户'

        if kwargs.get('phone'): 
            c.phone = kwargs.get('phone')
        if kwargs.get('name'):
            c.name = kwargs.get('name')
        if kwargs.get('password'):
            c.password = kwargs.get('password')
        if kwargs.get('state'):
            c.state = kwargs.get('state')
        if kwargs.get('role_id'):
            c.role_id = kwargs.get('role_id')
        db.session.add(c)
        db.session.commit()
        return True, ''

    @classmethod
    def add(cls, phone, password, name=""):
        manager = Manager(
                    phone = phone,
                    name = name,
                    password = password,
                    state = 0 
        )
        db.session.add(manager)
        db.session.commit()
        return manager


class FRole(Role):
    __abstract__ = True

    @classmethod
    def get(cls, _id):
        return db.session.query(Role).filter(Role.id==_id).first()

    @classmethod
    def query(cls, page, per_page):
        return db.session.query(Role)\
                         .filter(Role.en_name != 'superadmin')\
                         .paginate(page=page, per_page=per_page, error_out=False)

    @classmethod
    def name_is_exist(cls, en_name = None, name = None):
        r = db.session.query(Role).filter(Role.en_name == en_name).all()
        if r:
            return True
        
        r = db.session.query(Role).filter(Role.name == name).all()
        if r:
            return True

        return False

    @classmethod
    def add(cls, en_name, name, description, routes, permissions):
        if cls.name_is_exist(en_name, name):
            return False, '姓名或英文名称已存在'

        r = Role()
        r.en_name = en_name
        r.name = name
        r.description = description
        r.routes = routes
        db.session.add(r)
        db.session.commit()

        post_permissions = [FPermission.get(_id) for _id in permissions]
        r.permissions = list(filter(None, post_permissions))
        db.session.commit()
        return True, ''

    @classmethod
    def delete(cls, _id):
        p = cls.get(_id)
        db.session.delete(p)
        db.session.commit()

    @classmethod
    def modify(cls, _id, **kwargs):
        r = cls.get(_id)
        if not r:
            return False, '角色未找到'

        if kwargs.get('en_name'):
            if r.en_name != kwargs.get('en_name'):
                if cls.name_is_exist(en_name = kwargs.get('en_name')):
                    return False, '英文名称已存在'

            r.en_name = kwargs.get('en_name')
        if kwargs.get('name'):
            if r.name != kwargs.get('name'):
                if cls.name_is_exist(name = kwargs.get('name')):
                    return False, '姓名已存在'

            r.name = kwargs.get('name')
        if kwargs.get('description'):
            r.description = kwargs.get('description')
        if kwargs.get('routes'):
            r.routes = kwargs.get('routes')
        db.session.add(r)
        db.session.commit()
        
        if kwargs.get('permissions'):
            binded = r.permissions
            post_permissions = [FPermission.get(_id) for _id in kwargs.get('permissions')]
            post_permissions = list(filter(None, post_permissions))
            appends = list(set(post_permissions).difference(set(binded)))
            removes = list(set(binded).difference(set(post_permissions))) 
            for rm_obj in removes:
                if rm_obj in binded:
                    binded.remove(rm_obj)
            for ap_obj in appends:
                if ap_obj not in binded:
                    binded.append(ap_obj)
            db.session.commit()
        return True, ''

    @classmethod
    def get_name_ids(cls):
        roles = db.session.query(Role).filter(Role.en_name != 'superadmin').all()
        ret = []
        for item in roles:
            ret.append({
                        'role_id': item.id,
                        'role_name': item.name,
                        })
        return ret
        
    
class FPermission(Permission):
    __abstract__ = True

    @classmethod
    def get(cls, _id):
        return db.session.query(Permission).filter(Permission.id==_id).first()

    @classmethod
    def query(cls, page, per_page):
        return db.session.query(Permission).paginate(page=page, per_page=per_page, error_out=False)

    @classmethod
    def add(cls, name, method, uri):
        p = Permission()
        p.name = name
        p.method = method
        p.uri = uri
        db.session.add(p)
        db.session.commit()
        return True, ''

    @classmethod
    def delete(cls, _id):
        p = cls.get(_id)
        db.session.delete(p)
        db.session.commit()

    @classmethod
    def modify(cls, _id, **kwargs):
        r = cls.get(_id)
        if not r:
            return False, '权限未找到'

        if kwargs.get('name'):
            r.name = kwargs.get('name')
        if kwargs.get('method'):
            r.method = kwargs.get('method')
        if kwargs.get('uri'):
            r.uri = kwargs.get('uri')
        db.session.add(r)
        db.session.commit()
        return True, ''


class FAdminLog(AdminLog):
    __abstract__ = True

    @classmethod
    def query(cls, page, per_page, start, end):
        q = db.session.query(AdminLog).filter(AdminLog.state>0)\
                            .order_by(AdminLog.id.desc())
        if start:
            q.filter(AdminLog.create_time >= start)
        if end:
            q.filter(AdminLog.create_time < end)
        return q.paginate(page=page, per_page=per_page, error_out=False)

    @classmethod
    def add(cls, title, info):
        _log = AdminLog(title = title, info = info)
        db.session.add(_log)
        db.session.commit()
