import json
from werkzeug.security import check_password_hash
from flask import request, jsonify

from . import mod
from util.consts import *
from app.account.proc import *
from inc.retcode import RETCODE
from inc.decorator import jwt_required, verify_permission, current_identity


"""
@api {post} /account/login 登陆
@apiGroup Account
@apiVersion 1.0.0

@apiParam {String} username 登陆账号
@apiParam {String} password 密码

@apiSuccess {Number} id
@apiSuccess {String} username 用户登陆名称
"""
@mod.route('/login', methods=["POST"])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    if not username or not password:
        return jsonify(code=RETCODE.LOGINERR, message='请输入正确的用户名或密码')

    user = get_user_by_username(username)
    if not user:
        return jsonify(code=RETCODE.LOGINERR, message="未找到用户")

    isok, ret = user_login(user, password)
    if not isok:
        return jsonify(code=RETCODE.LOGINERR, message=ret)

    return jsonify(code=RETCODE.OK, data={'token': ret.decode('utf8')})


"""
@api {post} /account/regist 注册
@apiGroup Account
@apiVersion 1.0.0

@apiParam {String} username 登陆账号
@apiParam {String} name 真实姓名
@apiParam {String} phone 手机号
@apiParam {String} email 邮箱，如用于找回密码
@apiParam {String} password 密码

@apiSuccess {Number} id
@apiSuccess {String} username 用户登陆名称
"""
@mod.route('/regist', methods=['POST'])
def regist():
    username = request.json.get('username')
    name = request.json.get('name')
    phone = request.json.get('phone')
    email = request.json.get('email')
    password = request.json.get('password')
    if not username or not password:
        return jsonify(code=RETCODE.PARAMERR, message="请填写账号密码")

    user = get_user_by_username(username)
    if user:
        return jsonify(code=RETCODE.USERERR, message="此用户已注册")

    isok, organization = modify_organization(name=username, kind=1)
    if not isok:
        return jsonify(code=RETCODE.DATAERR, message="组织创建失败")

    isok, user = modify_user(None,
                            username = username,
                            name = name,
                            email = email,
                            phone = phone,
                            password = password,
                            role_id = ROLE_ADMIN_ID,
                            organization_id = organization.id)
    if not isok:
        return jsonify(code=RETCODE.DATAERR, message="注册失败")

    return jsonify(code=RETCODE.OK, data={})


"""
@api {post} /account/sub/add 添加子账户
@apiGroup Account
@apiVersion 1.0.0

@apiParam {String} username 登陆账号
@apiParam {String} name 真实姓名
@apiParam {String} phone 手机号
@apiParam {String} email 邮箱，如用于找回密码
@apiParam {String} password 密码
@apiParam {String} role_id 角色id
@apiParam {String} organization_id 组织id

@apiSuccess {Number} id
@apiSuccess {String} username 用户登陆名称
"""
@mod.route('/sub/add', methods=['POST'])
@jwt_required
def subaccount_add():
    username = request.json.get('username')
    name = request.json.get('name')
    phone = request.json.get('phone')
    email = request.json.get('email')
    password = request.json.get('password')
    role_id = request.json.get('role_id')
    if not username or not password:
        return jsonify(code=RETCODE.PARAMERR, message="请填写账号密码")

    user = get_user_by_username(username)
    if user:
        return jsonify(code=RETCODE.USERERR, message="此用户已注册")

    isok, user = modify_user(None,
                            username = username,
                            name = name,
                            email = email,
                            phone = phone,
                            password = password,
                            role_id = role_id,
                            organization_id = current_identity.get('organization_id'))
    if not isok:
        return jsonify(code=RETCODE.DATAERR, message="注册失败")

    return jsonify(code=RETCODE.OK, data={})


"""
@api {get} /account/list 获取用户列表
@apiGroup Account
@apiVersion 1.0.0    

@apiParam {String} organization_bid 组织id(选填，超级管理员使用这个参数，查看指定组织下的子用户，root下不填则查看所有用户)
@apiParam {String} name 真实姓名，支持模糊搜索
@apiParam {String} email 支持模糊搜索
@apiParam {String} phone 支持模糊搜索
@apiParam {String} username 登录名，支持模糊搜索
@apiParam {Number} page 页码，从1开始
@apiParam {Number} per_page 每页展示条数

@apiSuccess {Number} total 总数
@apiSuccess {Number} page
@apiSuccess {Number} per_page
@apiSuccess {Object[]} items
@apiSuccess {Number} items.bid
@apiSuccess {String} items.username 用户登陆名
@apiSuccess {String} items.name 真实姓名
@apiSuccess {String} items.email 用户邮箱
@apiSuccess {String} items.phone 用户手机号
@apiSuccess {String} items.organization_bid 组织bid
@apiSuccess {String} items.organization_name 组织名字
"""
@mod.route('/list')
@jwt_required
@verify_permission
def user_list():
    organization_bid = current_identity.get('organization_bid')
    if ORGANIZATION_SYS_ADMIN_ID == current_identity.get('organization_id'):
        organization_bid = request.args.get('organization_bid', None, type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    total, items = get_users(page, per_page,
                            organization_bid = organization_bid,
                            name = request.args.get('name'),
                            email = request.args.get('email'),
                            phone = request.args.get('phone'),
                            username = request.args.get('username'))
    return jsonify(code=RETCODE.OK, data={'items': items, 'total': total, 'page': page, 'per_page': per_page})


"""
@api {post} /account/modify 用户修改
@apiDescription 用户对自己账户的修改，admin对子账户的修改
@apiGroup Account
@apiVersion 1.0.0

@apiParam {Number} bid 用户bid
@apiParam {String} username 登陆账号
@apiParam {String} name 真实姓名
@apiParam {String} phone 手机号
@apiParam {String} email 邮箱，如用于找回密码
@apiParam {String} role_id 角色ID
@apiParam {String} password 密码，这里主要是admin对子账户的密码重置,用户自己修改密码则需单独页面，调用修改密码接口
"""
@mod.route('/modify', methods=['POST'])
@jwt_required
def user_modify():
    if not request.json.get('bid'):
        return jsonify(code=RETCODE.PARAMERR, message="缺少参数")

    isok, ret = modify_user(request.json.get('bid'),
                    user_id = current_identity.get('user_id'),
                    username = request.json.get('username'),
                    name = request.json.get('name'),
                    email = request.json.get('email'),
                    phone = request.json.get('phone'),
                    password = request.json.get('password'),
                    role_id = request.json.get('role_id'))
    if not isok:
        return jsonify(code=RETCODE.DATAERR, message=ret)

    return jsonify(code=RETCODE.OK, data={})


"""
@api {post} /account/del 用户删除
@apiGroup Account
@apiVersion 1.0.0

@apiParam {Number[]} bids 删除账号的数组,用户的bid
"""
@mod.route('/del', methods=['POST'])
@jwt_required
@verify_permission
def users_del():
    isok, ret = del_user(request.json.get('bids'))
    if not isok:
        return jsonify(code=RETCODE.DATAERR, message=ret)

    return jsonify(code=RETCODE.OK, data={})


"""
@api {get} /account/menu 获取用户目录列表
@apiGroup Account
@apiVersion 1.0.0

@apiSuccess {String[]} menus 目录如：[page1, page2]
"""
@mod.route('/menu')
@jwt_required
def user_menu():
    user_id = current_identity.get('user_id')
    menus = get_user_menu(user_id)
    return jsonify(code=RETCODE.OK, data={"menus": menus})


"""
@api {get} /account/role/list 获取角色列表
@apiGroup Account
@apiVersion 1.0.0    

@apiParam {Number} organization_bid
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
@jwt_required
@verify_permission
def role_list():
    organization_bid = current_identity.get('organization_bid')
    if ORGANIZATION_SYS_ADMIN_ID == current_identity.get('organization_id'):
        organization_bid = request.args.get('organization_bid', None, type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    total, items = get_roles(page, per_page,
                            organization_bid = organization_bid,
                            name = request.args.get('name'))
    return jsonify(code=RETCODE.OK, data={'items': items, 'total': total, 'page': page, 'per_page': per_page})


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
@jwt_required
@verify_permission
def role_modify():
    isok, ret = modify_role(request.json.get('id'),
                    organization_id = current_identity.get('organization_id'),
                    name = request.json.get('name'),
                    menu = request.json.get('menu'),
                    permissions = request.json.get('permissions'),
                    state = request.json.get('state'))
    if not isok:
        return jsonify(code=RETCODE.DATAERR, message=ret)

    return jsonify(code=RETCODE.OK, data={})


"""
@api {post} /account/role/del 角色删除
@apiGroup Account
@apiVersion 1.0.0

@apiParam {Number} id 角色id
"""
@mod.route('/role/del', methods=['POST'])
@jwt_required
@verify_permission
def role_del():
    isok, ret = del_role(request.json.get('id'))
    if not isok:
        return jsonify(code=RETCODE.DATAERR, message=ret)

    return jsonify(code=RETCODE.OK, data={})


"""
@api {get} /account/organization/list 获取组织列表
@apiGroup Account
@apiVersion 1.0.0

@apiParam {Number} page 页码，从1开始
@apiParam {Number} per_page 每页展示条数

@apiSuccess {Number} total 总数
@apiSuccess {Number} page
@apiSuccess {Number} per_page
@apiSuccess {Object[]} items
@apiSuccess {Number} items.bid
@apiSuccess {String} items.name 组织名称
@apiSuccess {Number} items.kind 组织类型，1:个人，2:组织
"""
@mod.route('/organization/list')
@jwt_required
@verify_permission
def organization_list():
    organization_bid = current_identity.get('organization_bid')
    if ORGANIZATION_SYS_ADMIN_ID == current_identity.get('organization_id'):
        organization_bid = request.args.get('organization_bid', None, type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    total, items = get_organizations(page, per_page,
                                    organization_bid = organization_bid,
                                    name = request.args.get('name'))
    return jsonify(code=RETCODE.OK, data={'items': items, 'total': total, 'page': page, 'per_page': per_page})


"""
@api {post} /account/organization/modify 组织信息修改
@apiGroup Account
@apiVersion 1.0.0

@apiParam {String} organization_bid 指定某个组织修改（root下必填，其他用户取所属组织信息）
@apiParam {String} name 名称
@apiParam {String} kind 1:个人,2:团体
"""
@mod.route('/organization/modify', methods=['POST'])
@jwt_required
@verify_permission
def organization_modify():
    if ORGANIZATION_SYS_ADMIN_ID == current_identity.get('organization_id'):
        organization_bid = request.json.get('organization_bid')
    else:
        organization_bid = current_identity.get("organization_bid")

    if not organization_bid:
        return jsonify(code=RETCODE.PARAMERR, message="参数异常")

    isok, ret = modify_organization(
                    organization_bid = organization_bid,
                    name = request.json.get('name'),
                    kind = request.json.get('kind'))
    if not isok:
        return jsonify(code=RETCODE.DATAERR, message=ret)

    return jsonify(code=RETCODE.OK, data={})


"""
@api {post} /account/password/modify 密码修改
@apiDescription 用户自己修改
@apiGroup Account
@apiVersion 1.0.0

@apiParam {String} password 旧密码
@apiParam {String} new_password 新密码
"""
@mod.route('/password/modify', methods=["POST"])
@jwt_required
def password_modify():
    isok, ret = modify_user(current_identity.get('user_bid'),
                            password = request.json.get('password'),
                            new_password = request.json.get('new_password'))
    if not isok:
        return jsonify(code=RETCODE.USERERR, message=ret)
        
    return jsonify(code=RETCODE.OK, data={})


"""
@api {post} /account/password/forget 忘记密码
@apiGroup Account
@apiVersion 1.0.0

@apiParam {String} username 登陆名
@apiParam {String} email 注册时绑定的邮箱（选填）
@apiParam {String} phone 注册时绑定的手机号（选填）
"""
@mod.route('/password/forget', methods=["POST"])
def password_forget():
    username = request.json.get('username')
    email = request.json.get('email')
    phone = request.json.get('phone')
    isok = check_email_phone(username=username, email=email, phone=phone)
    if not isok:
        return jsonify(code=RETCODE.USERERR, message="登录名或邮箱错误")

    send_code(email=email, phone=phone) # add async
    return jsonify(code=RETCODE.OK, data={})


"""
@api {post} /account/code/verify 验证码校验
@apiGroup Account
@apiVersion 1.0.0

@apiParam {String} email 邮箱（选填）
@apiParam {String} phone 手机号（选填）
@apiParam {String} code 验证码
@apiParam {String} password 修改后的新密码
"""
@mod.route('/code/verify', methods=["POST"])
def code_verify():
    email = request.json.get('email', '')
    phone = request.json.get('phone', '')
    code = request.json.get('code')
    password = request.json.get('password')
    if not email or not code or not password:
        return jsonify(code=RETCODE.PARAMERR, message="参数缺失")

    isok = check_code(email=email, phone=phone, code=code)
    if not isok:
        return jsonify(code=RETCODE.USERERR, message="请输入正确的验证码")
    
    user = get_user_by_email_or_phone(email, phone)
    if not user:
        return jsonify(code=RETCODE.USERERR, message="未找到此用户")
    isok, user = modify_user(user.bid, password = password)
    if not isok:
        return jsonify(code=RETCODE.USERERR, message=user)
    isok, err = user_login(user)
    if not isok:
        return jsonify(code=RETCODE.USERERR, message=err)

    return jsonify(code=RETCODE.OK, data={})


"""
@api {post} /account/loginout 退出登陆
@apiGroup Account
@apiVersion 1.0.0
"""
@mod.route('/loginout', methods=["POST"])
@jwt_required
def loginout():
    return jsonify(code=RETCODE.OK, data={})

