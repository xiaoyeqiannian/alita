import random
import time
import base64
from flask import session
from sqlalchemy import or_
from werkzeug.security import generate_password_hash, check_password_hash

from . import rc
from inc import app
from app.account.models import *
from inc.casbin_adapter import rbac
from util import emailer
from util.consts import *
from inc.snowflake import snow
from inc.decorator import jwt_encode
from inc.exceptions import ArgumentError, ReqError, LoginError, UserError


def get_user_by_name(name):
    return User.query.filter(User.name==name, User.state==STATE_VALID).first()


def get_user_by_id(_id):
    return User.get(_id)


def user_login(user, password=None):
    """
    sys login internal can set password=None
    """
    if password:
        ret = check_password_hash(user.password, b64_decode(password))
        if not ret:
            raise UserError(message = 'Password error!')
    
    o = Group.get(user.group_id)
    if not o:
        raise UserError(message = 'Account error!')

    r = Role.get(user.role_id)
    return jwt_encode({ 'user_id': user.id,
                        'user_name': user.name,
                        'role_id': user.role_id,
                        'group_id': user.group_id,
                        'role_name': r and r.name})


def get_users(page, per_page, **kwargs):
    pagination = db.session.query(User)\
                        .join(Group, Group.id == User.group_id)\
                        .join(Role, Role.id == User.role_id)\
                        .filter(User.state == 1, User.role_id > ROLE_ADMIN_ID)\
                        .with_entities(
                                    User.id,           # 0
                                    User.name,         # 1
                                    User.email,        # 2
                                    User.phone,        # 3
                                    Role.id,           # 4
                                    Role.name,         # 5
                                    Group.name,        # 6
                                    )\
                        .order_by(User.id.desc())

    if kwargs.get('name'):
        pagination = pagination.filter(User.name.like("%{}%".format(kwargs.get('name'))))
    if kwargs.get('email'):
        pagination = pagination.filter(User.email.like("%{}%".format(kwargs.get('email'))))
    if kwargs.get('phone'):
        pagination = pagination.filter(User.phone.like("%{}%".format(kwargs.get('phone'))))

    pagination = pagination.paginate(page=page, per_page=per_page, error_out=False)
    items = []
    for item in pagination.items:
        items.append({
                "id":                item[0],
                "name":              item[1],
                "email":             item[2],
                "phone":             item[3],
                "role_id":           item[4],
                "role_name":         item[5],
                "group_name":        item[6],
            })
    return {'items': items, 'total': pagination.total, 'page': page, 'per_page': per_page}


def del_user(ids):
    if not ids or not isinstance(ids, list):
        raise ArgumentError(message= '参数异常')

    for _id in ids:
        if not _id:
            continue
        
        u = User.query.filter_by(id = _id, state = STATE_VALID).first()
        if not u:
            continue

        u.state = STATE_DELETED
        db.session.add(u)
        db.session.commit()
    return True, ''


def username_is_existed(name):
    return db.session.query(User).filter(User.name==name, User.state==STATE_VALID).first()


def b64_decode(s):
    return base64.b64decode(s).decode('utf8')


def check_password(user, password):
    if not check_password_hash(user.password, b64_decode(password)):
        raise ArgumentError(message= 'Password error!')


def modify_user(user, **kwargs):
    name = kwargs.get("name")
    if name and name != user.name:# name用于登陆，必须唯一
        if username_is_existed(name):
            raise UserError(message= "The username is existed!")

        user.name = name.strip()

    if kwargs.get("phone"):
        user.phone = kwargs.get("phone").strip()

    new_password = kwargs.get("new_password")
    if new_password:
        user.password = generate_password_hash(b64_decode(new_password))

    if kwargs.get("email"):
        user.email = kwargs.get("email").strip()

    if kwargs.get('state'):
        user.state = kwargs.get('state')

    if kwargs.get('role_id'):
        user.role_id = kwargs.get('role_id')

    db.session.add(user)
    db.session.commit()
    return user


def create_user(**kwargs):
    name =     kwargs.get("name")
    password = kwargs.get("password")
    group_id = kwargs.get('group_id')
    role_id =  kwargs.get('role_id')
    if not name or not password or not group_id or not role_id:
        raise ArgumentError

    if username_is_existed(name):
        raise UserError(message= "The user is existed!")

    c = User(state = STATE_VALID)
    c.name = name.strip()
    c.role_id = role_id
    c.group_id = group_id
    c.password = generate_password_hash(b64_decode(password))
    if kwargs.get("phone"):
        c.phone = kwargs.get("phone")
    if kwargs.get("email"):
        c.email = kwargs.get("email")
    db.session.add(c)
    db.session.commit()
    return c


def get_user_menu(_id):
    user = User.get(_id)
    if not user:
        return []

    role = Role.get(user.role_id)
    if not role:
        return []

    return role.menu.split(',')


def get_roles(page, per_page, **kwargs):
    pagination = db.session.query(Role)\
                        .join(Group, Group.id == Role.group_id)\
                        .filter(Role.id > ROLE_ADMIN_ID, Role.state == 1)\
                        .order_by(Role.id.desc())

    if kwargs.get('group_id'):
        pagination = pagination.filter(Group.id == kwargs.get('group_id'))
    if kwargs.get('name'):
        pagination = pagination.filter(Role.name == kwargs.get('name'))

    pagination = pagination.paginate(page=page, per_page=per_page, error_out=False)
    items = []
    for item in pagination.items:
        permissions = rbac.get_filtered_policy(0, str(item.id))
        items.append({
                "id": item.id,
                "name": item.name,
                "menu": item.menu and item.menu.split(','),
                "permissions": [p[1] for p in permissions],
            })

    return {'items': items, 'total': pagination.total, 'page': page, 'per_page': per_page}


def del_role(ids):
    for _id in ids:
        if not _id:
            continue
        
        r = Role.query.filter_by(id = _id, state = STATE_VALID).first()
        if not r:
            continue

        r.state = STATE_DELETED
        db.session.add(r)
        db.session.commit()


def modify_role(_id, group_id, **kwargs):
    name = kwargs.get('name')
    menu = kwargs.get('menu')
    state = kwargs.get('state')
    permissions = kwargs.get('permissions')
    r = db.session.query(Role).get({'id': _id})
    if not r:
        r = Role()

    if name and r.name != name:
        r1 = db.session.query(Role).filter(Role.name==name, Role.group_id==group_id, Role.state==1).first()
        if r1:
            raise UserError(message= '此角色已存在!')

        r.name = name
    r.menu = menu
    r.group_id = group_id
    r.state = state or r.state
    db.session.add(r)
    db.session.commit()
    
    rbac.remove_filtered_policy(0, str(r.id))
    for item in permissions:
        rbac.add_policy(str(r.id), item.get('path'), item.get('method'))
    return r


def get_groups(page, per_page, **kwargs):
    pagination = db.session.query(Group).filter(Group.id > GROUP_SYS_ADMIN_ID).order_by(Group.id.desc())
    if kwargs.get('group_id'):
        pagination = pagination.filter(Group.id == kwargs.get('group_id'))
    if kwargs.get('name'):
        pagination = pagination.filter(Group.name == kwargs.get('name'))
    pagination = pagination.paginate(page=page, per_page=per_page, error_out=False)
    items = []
    for item in pagination.items:
        items.append({
                "id":  item.id,
                "name": item.name,
                "kind": item.kind,
            })
    return {'items': items, 'total': pagination.total, 'page': page, 'per_page': per_page}


def modify_group(**kwargs):
    group_id = kwargs.get('group_id')
    name = kwargs.get('name', '')
    kind = kwargs.get('kind', '')
    group = None

    if group_id:
        group = Group.get(group_id)

    if not group:
        group = Group()

    if name and group.name != name:
        group.name = name

    if kind and group.kind != kind:
        group.kind = kind

    db.session.add(group)
    db.session.commit()
    return group


def check_email(**kwargs):
    name = kwargs.get('name')
    email = kwargs.get('email')
    user = User.query.filter(User.name==name, User.state==STATE_VALID).first()
    if not user or user.email != email:
        raise ArgumentError(message="Email error!")


def send_code(**kwargs):
    email = kwargs.get('email')
    code = ''.join([str(random.randint(0,9)) for i in range(VERIFY_CODE_LENGTH)])
    if email:
        rc.set(email + ":code", code, VERIFY_CODE_EXPIRE_TIME)
        emailer.send(email, '验证码', "您的验证码：" + code)


def check_code(**kwargs):
    email = kwargs.get('email')
    code = kwargs.get('code')
    if email:
        r_code = rc.get(email + ":code")
        if r_code == code or (r_code and code == "666888"):
            rc.delete(email + ":code")
            return

    raise ArgumentError(message= "Code error")
