import json
from werkzeug.security import check_password_hash
from flask import request, jsonify

from . import mod
from util.consts import *
from app.account.proc import *
from inc.exceptions import ArgumentError, ReqError, LoginError, UserError
from inc.decorator import jwt_required, verify_permission, current_identity, except_handler


"""
@api {post} /account/login 登陆
@apiGroup Account
@apiVersion 1.0.0

@apiParam {String} name 登陆账号
@apiParam {String} password 密码

@apiSuccess {Number} id
@apiSuccess {String} name 用户登陆名称
"""
@mod.route('/login', methods=["POST"])
@except_handler
def login():
    name = request.json.get('name')
    password = request.json.get('password')
    if not name or not password:
        raise LoginError(message='请输入正确的用户名或密码')

    user = get_user_by_name(name)
    if not user:
        raise LoginError(message='未找到用户')

    token = user_login(user, password)
    return {'token': token.decode('utf8')}


"""
@api {post} /account/regist 注册
@apiGroup Account
@apiVersion 1.0.0

@apiParam {String} name 登陆账号
@apiParam {String} phone 手机号
@apiParam {String} email 邮箱，如用于找回密码
@apiParam {String} password 密码

@apiSuccess {Number} id
@apiSuccess {String} name 用户登陆名称
"""
@mod.route('/regist', methods=['POST'])
@except_handler
def regist():
    name = request.json.get('name')
    phone = request.json.get('phone')
    email = request.json.get('email')
    password = request.json.get('password')
    if not name or not password:
        raise ArgumentError(message='please input name or password')

    user = get_user_by_name(name)
    if user:
        raise UserError(message='This user is registed')

    group = modify_group(name=name, kind=1)
    if not group:
        raise DataError(message='Group create fail')

    modify_user(None,
                name = name,
                email = email,
                phone = phone,
                password = password,
                role_id = ROLE_ADMIN_ID,
                group_id = group.id)


"""
@api {post} /account/sub/add 添加子账户
@apiGroup Account
@apiVersion 1.0.0

@apiParam {String} name 登陆账号
@apiParam {String} phone 手机号
@apiParam {String} email 邮箱，如用于找回密码
@apiParam {String} password 密码
@apiParam {String} role_id 角色id
@apiParam {String} group_id 组织id

@apiSuccess {Number} id
@apiSuccess {String} name 用户登陆名称
"""
@mod.route('/sub/add', methods=['POST'])
@except_handler
@jwt_required
def subaccount_add():
    name = request.json.get('name')
    phone = request.json.get('phone')
    email = request.json.get('email')
    password = request.json.get('password')
    role_id = request.json.get('role_id')
    if not name or not password:
        raise ArgumentError(message='Please input name and password')

    user = get_user_by_name(name)
    if user:
        raise UserError(message='The user is registed')

    modify_user(None,
                name = name,
                email = email,
                phone = phone,
                password = password,
                role_id = role_id,
                group_id = current_identity.get('group_id'))


"""
@api {get} /account/list 获取用户列表
@apiGroup Account
@apiVersion 1.0.0    

@apiParam {String} group_id 组织id(选填，超级管理员使用这个参数，查看指定组织下的子用户，root下不填则查看所有用户)
@apiParam {String} name 登录名，支持模糊搜索
@apiParam {String} email 支持模糊搜索
@apiParam {String} phone 支持模糊搜索
@apiParam {Number} page 页码，从1开始
@apiParam {Number} per_page 每页展示条数

@apiSuccess {Number} total 总数
@apiSuccess {Number} page
@apiSuccess {Number} per_page
@apiSuccess {Object[]} items
@apiSuccess {String} items.name 用户登陆名
@apiSuccess {String} items.email 用户邮箱
@apiSuccess {String} items.phone 用户手机号
@apiSuccess {String} items.group_id 组织id
@apiSuccess {String} items.group_name 组织名字
"""
@mod.route('/list')
@except_handler
@jwt_required
@verify_permission
def user_list():
    group_id = current_identity.get('group_id')
    if GROUP_SYS_ADMIN_ID == group_id:
        group_id = request.args.get('group_id', None, type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    total, items = get_users(page, per_page,
                            group_id = group_id,
                            name = request.args.get('name'),
                            email = request.args.get('email'),
                            phone = request.args.get('phone'))
    return {'items': items, 'total': total, 'page': page, 'per_page': per_page}


"""
@api {post} /account/modify 用户修改
@apiDescription 用户对自己账户的修改，admin对子账户的修改
@apiGroup Account
@apiVersion 1.0.0

@apiParam {Number} user_id 用户id
@apiParam {String} name 登陆账号
@apiParam {String} phone 手机号
@apiParam {String} email 邮箱，如用于找回密码
@apiParam {String} role_id 角色ID
@apiParam {String} password 密码，这里主要是admin对子账户的密码重置,用户自己修改密码则需单独页面，调用修改密码接口
"""
@mod.route('/modify', methods=['POST'])
@except_handler
@jwt_required
def user_modify():
    user_id = request.json.get('user_id') or current_identity.get('user_id')
    if not user_id:
        raise ArgumentError(message='缺少参数')

    modify_user(user_id,
                user_id = current_identity.get('user_id'),
                name = request.json.get('name'),
                email = request.json.get('email'),
                phone = request.json.get('phone'),
                password = request.json.get('password'),
                role_id = request.json.get('role_id'))


"""
@api {post} /account/del 用户删除
@apiGroup Account
@apiVersion 1.0.0

@apiParam {Number[]} ids 删除账号的数组,用户的id
"""
@mod.route('/del', methods=['POST'])
@except_handler
@jwt_required
@verify_permission
def users_del():
    del_user(request.json.get('ids'))


"""
@api {get} /account/menu 获取用户目录列表
@apiGroup Account
@apiVersion 1.0.0

@apiSuccess {String[]} menus 目录如：[page1, page2]
"""
@mod.route('/menu')
@except_handler
@jwt_required
def user_menu():
    user_id = current_identity.get('user_id')
    menus = get_user_menu(user_id)
    return {"menus": menus}


"""
@api {get} /account/role/list 获取角色列表
@apiGroup Account
@apiVersion 1.0.0    

@apiParam {Number} group_id
@apiParam {String} name
@apiParam {Number} page 页码，从1开始
@apiParam {Number} per_page 每页展示条数

@apiSuccess {Number} total 总数
@apiSuccess {Number} page
@apiSuccess {Number} per_page
@apiSuccess {Object[]} items
@apiSuccess {Number} items.id
@apiSuccess {String} items.name 角色名称
@apiSuccess {String[]} items.menu 角色的目录列表
@apiSuccess {String[]} items.permissions 角色的权限列表
"""
@mod.route('/role/list')
@except_handler
@jwt_required
@verify_permission
def role_list():
    group_id = current_identity.get('group_id')
    if GROUP_SYS_ADMIN_ID == current_identity.get('group_id'):
        group_id = request.args.get('group_id', None, type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    total, items = get_roles(page, per_page,
                            group_id = group_id,
                            name = request.args.get('name'))
    return {'items': items, 'total': total, 'page': page, 'per_page': per_page}


"""
@api {post} /account/role/modify 角色信息修改/新建
@apiGroup Account
@apiVersion 1.0.0

@apiParam {Number} id 角色id，没有则不传，自动新建
@apiParam {String} name 名称
@apiParam {String} menu 后台目录，英文逗号隔开
@apiParam {Object[]} permissions 权限
@apiParam {String} permissions.path 访问uri,不含应用名称，如"/admin", 如："/role/list"
@apiParam {String} permissions.method "get" or "post"
@apiParam {Number} state 0:无效,1:有效,2:删除
"""
@mod.route('/role/modify', methods=['POST'])
@except_handler
@jwt_required
@verify_permission
def role_modify():
    modify_role(request.json.get('id'),
                group_id = current_identity.get('group_id'),
                name = request.json.get('name'),
                menu = request.json.get('menu'),
                permissions = request.json.get('permissions'),
                state = request.json.get('state'))


"""
@api {post} /account/role/del 角色删除
@apiGroup Account
@apiVersion 1.0.0

@apiParam {Number[]} ids 角色ids
"""
@mod.route('/role/del', methods=['POST'])
@except_handler
@jwt_required
@verify_permission
def role_del():
    del_role(request.json.get('ids'))


"""
@api {get} /account/group/list 获取组织列表
@apiGroup Account
@apiVersion 1.0.0

@apiParam {Number} page 页码，从1开始
@apiParam {Number} per_page 每页展示条数

@apiSuccess {Number} total 总数
@apiSuccess {Number} page
@apiSuccess {Number} per_page
@apiSuccess {Object[]} items
@apiSuccess {Number} items.id
@apiSuccess {String} items.name 组织名称
@apiSuccess {Number} items.kind 组织类型，1:个人，2:组织
"""
@mod.route('/group/list')
@except_handler
@jwt_required
@verify_permission
def group_list():
    group_id = current_identity.get('group_id')
    if GROUP_SYS_ADMIN_ID == group_id:
        group_id = request.args.get('group_id', None, type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    total, items = get_groups(page, per_page,
                                    group_id = group_id,
                                    name = request.args.get('name'))
    return {'items': items, 'total': total, 'page': page, 'per_page': per_page}


"""
@api {post} /account/group/modify 组织信息修改
@apiGroup Account
@apiVersion 1.0.0

@apiParam {String} group_id 指定某个组织修改（root下必填，其他用户取所属组织信息）
@apiParam {String} name 名称
@apiParam {String} kind 1:个人,2:团体
"""
@mod.route('/group/modify', methods=['POST'])
@except_handler
@jwt_required
@verify_permission
def group_modify():
    if GROUP_SYS_ADMIN_ID == current_identity.get('group_id'):
        group_id = request.json.get('group_id')
    else:
        group_id = current_identity.get("group_id")

    if not group_id:
        raise ArgumentError(message='参数异常')

    modify_group(
        group_id = group_id,
        name = request.json.get('name'),
        kind = request.json.get('kind'))


"""
@api {post} /account/password/modify 密码修改
@apiDescription 用户自己修改
@apiGroup Account
@apiVersion 1.0.0

@apiParam {String} password 旧密码
@apiParam {String} new_password 新密码
"""
@mod.route('/password/modify', methods=["POST"])
@except_handler
@jwt_required
def password_modify():
    modify_user(current_identity.get('user_id'),
                password = request.json.get('password'),
                new_password = request.json.get('new_password'))


"""
@api {post} /account/password/forget 忘记密码
@apiGroup Account
@apiVersion 1.0.0

@apiParam {String} name 登陆名
@apiParam {String} email 注册时绑定的邮箱（选填）
@apiParam {String} phone 注册时绑定的手机号（选填）
"""
@mod.route('/password/forget', methods=["POST"])
@except_handler
def password_forget():
    name = request.json.get('name')
    email = request.json.get('email')
    phone = request.json.get('phone')
    check_email_phone(name=name, email=email, phone=phone)
    send_code(email=email, phone=phone)


"""
@api {post} /account/code/verify 验证码校验
@apiGroup Account
@apiVersion 1.0.0

@apiParam {String} name 登录名
@apiParam {String} email 邮箱（选填）
@apiParam {String} code 验证码
@apiParam {String} password 修改后的新密码
"""
@mod.route('/code/verify', methods=["POST"])
@except_handler
def code_verify():
    name = request.json.get('name', '')
    email = request.json.get('email', '')
    code = request.json.get('code')
    password = request.json.get('password')
    if not name or not email or not code or not password:
        raise ArgumentError(message='参数缺失')

    check_code(email=email, code=code)
    user = get_user_by_name(name)
    if not user:
        raise UserError(message='未找到此用户')

    modify_user(user.id, password = password)
    user_login(user)


"""
@api {post} /account/logout 退出登陆
@apiGroup Account
@apiVersion 1.0.0
"""
@mod.route('/logout', methods=["POST"])
@except_handler
@jwt_required
def logout():
    return {}

