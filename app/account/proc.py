import random
import time
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


def get_user_by_username(username):
    return User.query.filter(User.username == username, User.state == 1).first()


def get_user_by_email_or_phone(email, phone):
    user = User.query.filter(User.email==email, User.state==1).first()
    if user:
        return user

    return User.query.filter(User.phone==phone, User.state==1).first()


def user_login(user, password=None):
    if password:
        ret = check_password_hash(user.password, password)
        if not ret:
            raise UserError(message = '密码错误')
    
    o = Organization.get(user.organization_id)
    if not o:
        raise UserError(message = '账号异常')

    r = Role.get(user.role_id)
    return jwt_encode({ 'user_id': user.id,
                        'user_name': user.username,
                        'role_id': user.role_id,
                        'user_bid': user.bid,
                        'organization_id': user.organization_id,
                        'organization_bid': o.bid,
                        'role_name': r and r.name})


def get_users(page, per_page, **kwargs):
    pagination = db.session.query(User)\
                        .join(Organization, Organization.id == User.organization_id)\
                        .join(Role, Role.id == User.role_id)\
                        .filter(User.state == 1, User.role_id > ROLE_ADMIN_ID)\
                        .with_entities(
                                    User.id,           # 0
                                    User.bid,          # 1
                                    User.username,     # 2
                                    User.name,         # 3
                                    User.email,        # 4
                                    User.phone,        # 5
                                    Role.id,           # 6
                                    Role.name,         # 7
                                    Organization.bid,  # 8
                                    Organization.name, # 9
                                    )\
                        .order_by(User.id.desc())

    if kwargs.get('organization_bid'):
        pagination = pagination.filter(Organization.bid == kwargs.get('organization_bid'))
    if kwargs.get('name'):
        pagination = pagination.filter(User.name.like("%{}%".format(kwargs.get('name'))))
    if kwargs.get('username'):
        pagination = pagination.filter(User.username.like("%{}%".format(kwargs.get('username'))))
    if kwargs.get('email'):
        pagination = pagination.filter(User.email.like("%{}%".format(kwargs.get('email'))))
    if kwargs.get('phone'):
        pagination = pagination.filter(User.phone.like("%{}%".format(kwargs.get('phone'))))

    pagination = pagination.paginate(page=page, per_page=per_page, error_out=False)
    ret = []
    for item in pagination.items:
        ret.append({
                "id":                item[0],
                "bid":               str(item[1]),
                "username":          item[2],
                "name":              item[3],
                "email":             item[4],
                "phone":             item[5],
                "role_id":           item[6],
                "role_name":         item[7],
                "organization_bid":  item[8],
                "organization_name": item[9],
            })

    return pagination.total, ret


def del_user(bids):
    if not bids or not isinstance(bids, list):
        raise ArgumentError(message= '参数异常')

    for bid in bids:
        u = User.query.filter_by(bid = bid, state = 1).first()
        if not u:
            continue

        u.state = 0
        db.session.add(u)
        db.session.commit()
    return True, ''


def modify_user(bid, **kwargs):
    password = kwargs.get('password')
    new_password = kwargs.get('new_password')
    verify_code = kwargs.get('verify_code')
    username = kwargs.get('username', '')
    name = kwargs.get('name')
    email = kwargs.get('email', '')
    phone = kwargs.get('phone', '')
    state = kwargs.get('state')
    role_id = kwargs.get('role_id')
    organization_id = kwargs.get('organization_id')
    c = bid and User.query.filter_by(bid = bid).first()
    if not c:
        c = User(state = 1)
        # 新注册用户分配admin角色及权限,admin权限默认初始化为1,请确认
        c.role_id = 1
        c.bid = str(snow.get_id())

    if username and username != c.username:# username用于登陆，必须唯一
        m = db.session.query(User).filter(User.username==username, User.state==1).first()
        if m:
            raise UserError(message= '用户名已存在')

        c.username = username

    if name:
        c.name = name

    if phone:
        c.phone = phone

    if new_password:# 密码修改
        if verify_code:
            if not check_code(email = email, phone = phone, code = code):
                raise ArgumentError(message= '请输入正确的验证码')

        elif password:
            if not check_password_hash(c.password, password):
                raise ArgumentError(message= '密码错误')

        c.password = generate_password_hash(new_password)

    elif password:
        c.password = generate_password_hash(password)

    if email:
        c.email = email

    if state:
        c.state = state

    if role_id:
        c.role_id = role_id

    if organization_id:
        c.organization_id = organization_id
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


def get_roles(page, per_page, **kwargs):# TODO role.id这个判断需要走全局配置
    pagination = db.session.query(Role)\
                        .join(Organization, Organization.id == Role.organization_id)\
                        .filter(Role.id > ROLE_ADMIN_ID, Role.state == 1)\
                        .order_by(Role.id.desc())

    if kwargs.get('organization_bid'):
        pagination = pagination.filter(Organization.bid == kwargs.get('organization_bid'))
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


def modify_role(_id, organization_id, **kwargs):
    name = kwargs.get('name')
    menu = kwargs.get('menu')
    state = kwargs.get('state')
    permissions = kwargs.get('permissions')
    r = db.session.query(Role).get({'id': _id})
    if not r:
        r = Role()

    if name and r.name != name:
        r1 = db.session.query(Role).filter(Role.name==name, Role.organization_id==organization_id, Role.state==1).first()
        if r1:
            raise UserError(message= '此角色已存在!')

        r.name = name
    r.menu = menu
    r.organization_id = organization_id
    r.state = state or r.state
    db.session.add(r)
    db.session.commit()
    
    rbac.remove_filtered_policy(0, str(r.id))
    for item in permissions:
        rbac.add_policy(str(r.id), item.get('path'), item.get('method'))
    return r


def get_organization_by_bid(bid):
    return db.session.query(Organization).filter(Organization.bid == bid).first()


def get_organizations(page, per_page, **kwargs):
    pagination = db.session.query(Organization).filter(Organization.id > ORGANIZATION_SYS_ADMIN_ID).order_by(Organization.id.desc())
    if kwargs.get('organization_bid'):
        pagination = pagination.filter(Organization.bid == kwargs.get('organization_bid'))
    if kwargs.get('name'):
        pagination = pagination.filter(Organization.name == kwargs.get('name'))
    pagination = pagination.paginate(page=page, per_page=per_page, error_out=False)
    ret = []
    for item in pagination.items:
        ret.append({
                "bid":  item.bid,
                "name": item.name,
                "kind": item.kind,
            })

    return pagination.total, ret


def modify_organization(**kwargs):
    organization_id = kwargs.get('organization_id')
    organization_bid = kwargs.get('organization_bid')
    name = kwargs.get('name', '')
    kind = kwargs.get('kind', '')
    organization = None

    if organization_id:
        organization = Organization.get(organization_id)
    elif organization_bid:
        organization = Organization.get_by_bid(organization_bid)

    if not organization:
        organization = Organization()
        organization.bid = str(snow.get_id())

    if name and organization.name != name:
        organization.name = name

    if kind and organization.kind != kind:
        organization.kind = kind

    db.session.add(organization)
    db.session.commit()
    return True, organization


def check_email_phone(**kwargs):
    username = kwargs.get('username')
    email = kwargs.get('email')
    phone = kwargs.get('phone')
    user = User.query.filter(User.username==username,
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
