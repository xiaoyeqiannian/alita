# coding: utf-8

import logging
from . import mod, csrf
from flask import jsonify, request, render_template, url_for, redirect
from flask_login import login_user, logout_user, current_user
from app.admin.proce import *
from inc.retcode import RETCODE
from wtforms import Form
from app.admin.view_util import verify_permission

logger = logging.getLogger(__name__)


@mod.route('/login', methods=['GET', 'POST'])
def login():
    csrf.protect()
    if request.method == 'POST':
        phone = request.form.get('phone', '')
        password = request.form.get('password', '')
        if len(phone) == 0 or len(password) == 0:
            error = 'need phone number and password'
            return render_template('login.html', **locals())

        manager = get_manager_by_phone(phone)
        if not manager:
            error = "cann't find this manager"
        elif manager.state <= 0:
            error = 'invalid manager'
        elif hmac_encrypt(password) != manager.password.encode('utf8'):
            error = 'invalid password'
        else:
            login_user(manager)
            add_log('login', 'manager:%s,phone:%s' % (current_user.id, current_user.phone))
            next = request.args.get('next')
            return redirect(next or url_for('admin.admin_index'))

    return render_template('login.html', **locals())


@csrf.exempt
@mod.route('/logout', methods=['POST'])
@verify_permission
def logout():
    permission = ''
    add_log('logout', 'manager:%s,phone:%s' % (current_user.id, current_user.phone))
    logout_user()
    return jsonify(code=RETCODE.OK, data={})


@csrf.exempt
@mod.route('/regist', methods=['POST'])
def regist():
    phone = request.form.get('phone', '')
    password = request.form.get('password', '')
    if len(phone) == 0 or len(password) == 0:
        return jsonify(code=RETCODE.PARAMERR, error="need phone number and password")

    manager = get_manager_by_phone(phone)
    if manager:
        return jsonify(code=RETCODE.USERERR, error="this manager is registed")

    manager = regist_manager(phone, password)
    if not manager:
        return jsonify(code=RETCODE.DATAERR, error="regist fail")

    add_log('regist', 'manager:%s,phone:%s' % (manager.id, manager.phone))
    return jsonify(code=RETCODE.OK, data={})


@mod.route('/index')
@verify_permission
def admin_index():
    permission = ''
    user_count = get_user_total_count()
    business_volume = 2233
    visit_count = 1123243
    order_count = 121212
    return render_template('index.html', **locals())


@mod.route('/visit/statistics')
@verify_permission
def visit_statistics():
    permission = ''
    # just for test
    data = {'x_data': ['Jan','Feb','Mar','Apr','May','June'],
            'data': [100, 243, 323, 424, 667, 133]}
    return jsonify(code=RETCODE.OK, data=data) 


@mod.route('/visit/source/list')
@verify_permission
def source_list():
    permission = ''
    # just for test
    data = {'sources': ['wechat', 'weibo', 'baidu'],
            'mix_data': [1,2,3]}
    return jsonify(code=RETCODE.OK, data=data) 


@mod.route('/user', methods=['GET', 'POST'])
@verify_permission
def admin_user():
    permission = '1'
    if request.method == 'POST':
        user_id = request.form.get('id', None, type=int)
        phone = request.form.get('phone')
        name = request.form.get('name')
        pwd = request.form.get('pwd')
        role_id = request.form.get('role_id', None, type=int)
        state = request.form.get('state', None, type=int)
        isok, ret = modify_manager(user_id, phone=phone,
                                            name=name,
                                            pwd=pwd,
                                            role_id=role_id,
                                            state=state)
        if not isok:
            return jsonify(code=RETCODE.USERERR, error=ret)
            
        return jsonify(code=RETCODE.OK, data={}) 
    
    if request.args.get('download'):
        return get_manager_download() 
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    pagination, managers = get_managers(page, per_page)
    return render_template('user.html', **locals())


@mod.route('/role', methods=['GET', 'POST'])
@verify_permission
def admin_role():
    permission = '1'
    if request.method == 'POST':
        role_id = request.form.get('id', None, type=int)
        _method = request.form.get('_method')
        if _method == 'delete':
            del_role(role_id)
            return jsonify(code=RETCODE.OK, data={}) 

        en_name = request.form.get('en_name')
        name = request.form.get('name')
        description = request.form.get('description')
        routes = request.form.get('routes')
        permissions = request.form.getlist('permissions[]')
        if not role_id and (not en_name or not name or not routes or not permissions):
            return jsonify(code=RETCODE.PARAMERR, error="please complate")

        isok, ret = modify_role(role_id, en_name=en_name,
                                         name=name,
                                         description=description,
                                         routes=routes,
                                         permissions=permissions)
        if not isok:
            return jsonify(code=RETCODE.DATAERR, error=ret)

        return jsonify(code=RETCODE.OK, data={}) 
        
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    pagination, roles = get_roles(page, per_page)
    return render_template('role.html', **locals())


@mod.route('/role/list')
@verify_permission
def get_user_role_list():
    permission = '1'
    roles = get_role_name_list()
    return jsonify(code=RETCODE.OK, data=roles) 


@mod.route('/permission', methods=['GET', 'POST'])
@verify_permission
def admin_permission():
    permission = '1'
    if request.method == 'POST':
        pid = request.form.get('id', None, type=int)
        _method = request.form.get('_method')
        if _method == 'delete':
            del_permission(pid)
            return jsonify(code=RETCODE.OK, data={}) 

        name = request.form.get('name')
        method = request.form.get('method')
        uri = request.form.get('uri')
        if not pid and (not name or not method or not uri):
            return jsonify(code=RETCODE.PARAMERR, error="please complate and try again")

        isok, ret = modify_permission(pid, name=name,
                                           method=method,
                                           uri=uri)
        if not isok:
            return jsonify(code=RETCODE.DATAERR, error=ret)

        return jsonify(code=RETCODE.OK, data={}) 
        
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    pagination, permissions = get_permissions(page, per_page)
    return render_template('permission.html', **locals())


@mod.route('/permission/list')
@verify_permission
def permission_list():
    permission = '1'
    data = get_permission_list()
    return jsonify(code=RETCODE.OK, data=data)


@mod.route('/permission/selected')
@verify_permission
def permission_selected():
    permission = '1'
    role_id = request.args.get('role_id', None, type=int)
    data = get_permission_selected(role_id)
    return jsonify(code=RETCODE.OK, data=data)


@mod.route('/log')
@verify_permission
def admin_log():
    permission = '2'
    if request.args.get('download'):
        return get_log_download()

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    start = request.args.get('start')
    end = request.args.get('end')
    pagination, logs = get_logs(page, per_page, start, end)
    return render_template('log.html', **locals())
