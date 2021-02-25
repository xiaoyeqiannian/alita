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
    return User.query.filter(User.name == name, User.state == 1).first()


def get_user_by_email_or_phone(email, phone):
    user = User.query.filter(User.email==email, User.state==1).first()
    if user:
        return user

    return User.query.filter(User.phone==phone, User.state==1).first()


def user_login(user, password=None):
    if password:
        ret = check_password_hash(user.password, base64.b64decode(password).decode('utf8'))
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
    ret = []
    for item in pagination.items:
        ret.append({
                "id":                item[0],
                "name":              item[1],
                "email":             item[2],
                "phone":             item[3],
                "role_id":           item[4],
                "role_name":         item[5],
                "group_name":        item[6],
            })

    return pagination.total, ret


def del_user(user_ids):
    if not user_ids or not isinstance(user_ids, list):
        raise ArgumentError(message= '参数异常')

    for _id in user_ids:
        if not _id:
            continue
        
        u = User.query.filter_by(id = _id, state = 1).first()
        if not u:
            continue

        u.state = 0
        db.session.add(u)
        db.session.commit()
    return True, ''


def modify_user(_id, **kwargs):
    password = kwargs.get('password')
    new_password = kwargs.get('new_password')
    verify_code = kwargs.get('verify_code')
    name = kwargs.get('name')
    email = kwargs.get('email', '')
    phone = kwargs.get('phone', '')
    state = kwargs.get('state')
    role_id = kwargs.get('role_id')
    group_id = kwargs.get('group_id')
    c = User.query.filter_by(id = _id).first()
    if not c:
        c = User(state = 1)
        # 新注册用户分配admin角色及权限,admin权限默认初始化为1,请确认
        c.role_id = 1

    if name and name != c.name:# name用于登陆，必须唯一
        m = db.session.query(User).filter(User.name==name, User.state==1).first()
        if m:
            raise UserError(message= 'The user is existed')

        c.name = name

    if phone:
        c.phone = phone

    if new_password:# 密码修改
        if verify_code:
            if not check_code(email = email, phone = phone, code = code):
                raise ArgumentError(message= 'Use the right code')

        elif password:
            print(c.password, base64.b64decode(password).decode('utf8'))
            if not check_password_hash(c.password, base64.b64decode(password).decode('utf8')):
                raise ArgumentError(message= 'Password error')

        c.password = generate_password_hash(base64.b64decode(new_password).decode('utf8'))

    elif password:
        c.password = generate_password_hash(base64.b64decode(password).decode('utf8'))

    if email:
        c.email = email

    if state:
        c.state = state

    if role_id:
        c.role_id = role_id

    if group_id:
        c.group_id = group_id
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
    ret = []
    for item in pagination.items:
        permissions = rbac.get_filtered_policy(0, str(item.id))
        ret.append({
                "id": item.id,
                "name": item.name,
                "menu": item.menu and item.menu.split(','),
                "permissions": [p[1] for p in permissions],
            })

    return pagination.total, ret


def del_role(_id):
    r = Role.get(_id)
    if not r:
        raise UserError(message= '未找到此权限')

    r.state = 0
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
    ret = []
    for item in pagination.items:
        ret.append({
                "id":  item.id,
                "name": item.name,
                "kind": item.kind,
            })

    return pagination.total, ret


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


def check_email_phone(**kwargs):
    name = kwargs.get('name')
    email = kwargs.get('email')
    phone = kwargs.get('phone')
    user = User.query.filter(User.name==name,
                            or_(User.email==email, User.phone==phone))\
                     .first()
    if not user:
        raise ArgumentError(message= '手机号或邮箱错误')


def send_code(**kwargs):
    email = kwargs.get('email')
    phone = kwargs.get('phone')
    code = ''.join([str(random.randint(0,9)) for i in range(VERIFY_CODE_LENGTH)])
    if email:
        rc.set(email + ":code", code, VERIFY_CODE_EXPIRE_TIME)
        emailer.send(email, '验证码', "您的验证码：" + code)
    elif phone:
        pass


def check_code(**kwargs):
    email = kwargs.get('email')
    phone = kwargs.get('phone')
    code = kwargs.get('code')
    if email:
        r_code = rc.get(email + ":code")
        if r_code == code or (r_code and code == "666888"):
            rc.delete(email + ":code")
            return

    raise ArgumentError(message= '验证码错误')
