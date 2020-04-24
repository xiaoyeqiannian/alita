import time
import logging
from datetime import datetime, date, timedelta
from sqlalchemy import or_
from flask_login import login_user
from werkzeug.security import generate_password_hash, check_password_hash
from util.dateutil import date2string
from util import make_excel_online
from app.admin.models import *
from app.admin import login_manager

logger = logging.getLogger(__name__)


@login_manager.user_loader
def load_user(user_id):
    manager = Manager.get(user_id)
    return manager


def get_user_total_count():
    # just for test
    return 200


def get_managers(page, per_page, **kwargs):
    q = db.session.query(Manager)
    if kwargs.get('manager_id'):
        q = q.filter(Manager.id == kwargs.get('manager_id'))

    if kwargs.get('name') and kwargs.get('name')!='superadmin':
        q = q.filter(Manager.name.like("%{}%".format(kwargs.get('name'))))
    else:
        q = q.filter(Manager.name != 'superadmin')

    if kwargs.get('state'):
        q = q.filter(Manager.state == kwargs.get('state'))

    pagination = q.order_by(Manager.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return pagination, pagination.items


def get_manager_download():
    header = ['ID', 'name', 'role-id', 'role-name', 'state', 'create_time']
    ret = []
    for page in range(1000):
        pagination, items = get_managers(page, 20)
        for item in items:
            ret.append([
                    item.id,
                    item.name,
                    item.role_id,
                    item.role and item.role.name,
                    item.state_cn,
                    item.create_time and date2string(item.create_time) or '-',
                    ])
        if not pagination.has_next:
            break

    response = make_excel_online("user_list", header, ret)
    response.headers['Content-Type'] = "utf-8"
    response.headers["Cache-Control"] = "no-cache"
    response.headers["Content-Disposition"] = "attachment; filename=user%s.xlsx" % int(time.time())
    return response 


def manager_login(name, password):
    manager = get_manager_by_name(name)
    if not manager:
        return False, "cann't find this manager"

    elif manager.state <= 0:
        return False, 'invalid manager'

    elif not check_password_hash(manager.password, password):
        return False, 'invalid password'

    login_user(manager)
    add_log(manager.id, 'login', 'name:{}'.format(manager.name))
    return True, '' 


def modify_manager(_id, **kwargs):
    password = kwargs.get('pwd')
    if password:
        kwargs['password'] = generate_password_hash(password)
    c = Manager.get(_id)
    if not c:
        return False, "cann't find this user"

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


def get_manager_by_name(name):
    return db.session.query(Manager).filter(Manager.name==name).first() 


def regist_manager(name, password):
    manager = Manager(
                name = name,
                password = password,
                state = 0
    )
    db.session.add(manager)
    db.session.commit()
    return manager


def modify_manager_info(_id, **kwargs):
    c = Manager.get(_id)
    if not c:
        return False, "cann't find this user"

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


def get_roles(page, per_page):
    pagination = db.session.query(Role)\
                         .filter(Role.en_name != 'superadmin')\
                         .paginate(page=page, per_page=per_page, error_out=False)

    return pagination, pagination.items

def del_role(_id):
    p = db.session.query(Role).filter(Role.id==_id).first() 
    if not p:
        return

    db.session.delete(p)
    db.session.commit()

def modify_role(_id, **kwargs):
    if not _id:
        r = db.session.query(Role).filter(or_(Role.en_name==kwargs['en_name'], Role.name == kwargs['name'])).first()
        if r:
            return False, 'the role is exist'

        r = Role(en_name = kwargs['en_name'], name = kwargs['name'], description = kwargs['description'], routes = kwargs['routes'])
        db.session.add(r)
        db.session.commit()

        if kwargs['permissions']:
            post_permissions = [db.session.query(Permission).filter(Permission.id==_id).first() for _id in kwargs['permissions']]
            r.permissions = list(filter(None, post_permissions))
            db.session.commit()
        return True, r

    r = db.session.query(Role).filter(Role.id==_id).first()
    if not r:
        return False, "cann't find this role"

    if kwargs.get('en_name'):
        if r.en_name != kwargs.get('en_name'):
            r = db.session.query(Role).filter(Role.en_name==en_name).first()
            if r:
                return False, 'the english name is existed'

        r.en_name = kwargs.get('en_name')
    if kwargs.get('name'):
        if r.name != kwargs.get('name'):
            r = db.session.query(Role).filter(Role.name==name).first()
            if r:
                return False, 'the name is existed'

        r.name = kwargs.get('name')
    if kwargs.get('description'):
        r.description = kwargs.get('description')
    if kwargs.get('routes'):
        r.routes = kwargs.get('routes')
    db.session.add(r)
    db.session.commit()
    
    if kwargs.get('permissions'):
        binded = r.permissions
        post_permissions = [db.session.query(Permission).filter(Permission.id==_id).first() for _id in kwargs.get('permissions')]
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
    return True, r 


def get_role_name_list():
    roles = db.session.query(Role).filter(Role.en_name != 'superadmin').all()
    ret = []
    for item in roles:
        ret.append({ 'role_id': item.id, 'role_name': item.name })
    return ret 


def get_permissions(page, per_page):
    pagination = db.session.query(Permission).paginate(page=page, per_page=per_page, error_out=False)
    return pagination, pagination.items


def get_permission_list():
    pagination, items = get_permissions(1, 9999) 
    ret = []
    for item in items:
        tmp = {'id': item.id, 'text': item.name}
        ret.append(tmp)
    return ret


def get_permission_selected(_id):
    role = db.session.query(Role).filter(Role.id==_id).first()
    ret = []
    if not role:
        return ret

    for item in role.permissions:
        ret.append(item.id)
    return ret


def del_permission(_id):
    p = db.session.query(Permission).filter(Permission.id==_id).first()
    if not p:
        return

    db.session.delete(p)
    db.session.commit()


def modify_permission(_id, **kwargs):
    if not _id:
        p = Permission(name = kwargs['name'], method = kwargs['method'], uri = kwargs['uri'])
        """
        p.name = kwargs['name']
        p.method = kwargs['method']
        p.uri = kwargs['uri']
        """
        db.session.add(p)
        db.session.commit()
        return True, p
    else:
        p = db.session.query(Permission).filter(Permission.id==_id).first()
        if not p:
            return False, "cann't find this permission"

        if kwargs.get('name'):
            p.name = kwargs.get('name')
        if kwargs.get('method'):
            p.method = kwargs.get('method')
        if kwargs.get('uri'):
            p.uri = kwargs.get('uri')
        db.session.add(p)
        db.session.commit()
        return True, p


def get_logs(mid, page, per_page, start=None, end=None):
    q = db.session.query(AdminLog)\
                        .filter(AdminLog.state > 0)\
                        .order_by(AdminLog.id.desc())
    m = Manager.get(mid)
    if m.name != 'superadmin':
        q = q.filter(AdminLog.creator_id == mid)
    if start:
        q = q.filter(AdminLog.create_time >= start)
    if end:
        q = q.filter(AdminLog.create_time < end)
    pagination = q.paginate(page=page, per_page=per_page, error_out=False)
    return pagination, pagination.items


def get_log_download(mid):
    header = ['ID', 'title', 'info', 'create_time', 'creator_id']
    ret = []
    for page in range(1000):
        pagination, items = get_logs(mid, page, 20)
        for item in items:
            ret.append([
                    item.id,
                    item.title,
                    item.info,
                    date2string(item.create_time),
                    item.creator_id
                    ])
        if not pagination.has_next:
            break

    response = make_excel_online("log_list", header, ret)
    response.headers['Content-Type'] = "utf-8"
    response.headers["Cache-Control"] = "no-cache"
    response.headers["Content-Disposition"] = "attachment; filename=log%s.xlsx" % int(time.time())
    return response


def add_log(mid, title, info):
    _log = AdminLog(creator_id = mid, title = title, info = info)
    db.session.add(_log)
    db.session.commit()
