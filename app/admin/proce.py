# coding: utf-8

import re
import time
import logging
import xlsxwriter
from io import BytesIO
from flask import make_response
from datetime import datetime, date, timedelta
from app.admin.fusion import * 
from util.encrypt import hmac_encrypt
from util.dateutil import date2string


logger = logging.getLogger(__name__)


def make_excel(name, title, data):
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    p = re.compile(r'[/\?:：\*\[\]]')
    name = re.sub(p,"",name)
    worksheet = workbook.add_worksheet(name)
    worksheet.write_row('A1', title)
    for i in range(len(data)):
        worksheet.write_row('A' + str(i + 2), data[i])
    workbook.close()
    response = make_response(output.getvalue())
    output.close()
    return response


def get_user_total_count():
    # just for test
    return 200

def get_managers(page, per_page):
    pagination = FManager.query(page, per_page)
    return pagination, pagination.items


def create_manager_excel():
    header = ['ID', 'name', 'role-id', 'role-name', 'state', 'create_time']
    ret = []
    for page in range(1000):
        pagination = FManager.query(page, 20)
        for item in pagination.items:
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

    return make_excel("user_list", header, ret)


def get_manager_download():
    response = create_manager_excel() 
    response.headers['Content-Type'] = "utf-8"
    response.headers["Cache-Control"] = "no-cache"
    response.headers["Content-Disposition"] = "attachment; filename=user%s.xlsx" % int(time.time())
    return response 


def modify_manager(_id, **kwargs):
    password = kwargs.get('pwd')
    if password:
        kwargs['password'] = hmac_encrypt(password)
    return FManager.modify(_id, **kwargs)


def get_manager_by_name(name):
    return FManager.get_by_name(name)


def regist_manager(name, password):
    return FManager.add(name, hmac_encrypt(password))


def modify_manager_info(_id, **kwargs):
    return FManager.modify(_id, **kwargs)


def get_roles(page, per_page):
    pagination = FRole.query(page, per_page)
    return pagination, pagination.items

def del_role(_id):
    return FRole.delete(_id)

def modify_role(_id, **kwargs):
    if not _id:
        return FRole.add(kwargs['en_name'], kwargs['name'], kwargs['description'], kwargs['routes'], kwargs['permissions'])
    else:
        return FRole.modify(_id, **kwargs)


def get_role_name_list():
    return FRole.get_name_ids()


def get_permissions(page, per_page):
    pagination = FPermission.query(page, per_page)
    return pagination, pagination.items


def get_permission_list():
    pagination = FPermission.query(1, 999)
    ret = []
    for item in pagination.items:
        tmp = {'id': item.id, 'text': item.name}
        ret.append(tmp)
    return ret


def get_permission_selected(role_id):
    role = FRole.get(role_id)
    ret = []
    if not role:
        return ret

    for item in role.permissions:
        ret.append(item.id)
    return ret


def del_permission(_id):
    return FPermission.delete(_id)


def modify_permission(_id, **kwargs):
    if not _id:
        return FPermission.add(kwargs['name'], kwargs['method'], kwargs['uri'])
    else:
        return FPermission.modify(_id, **kwargs)


def get_logs(mid, page, per_page, start, end):
    pagination = FAdminLog.query(mid, page, per_page, start, end)
    return pagination, pagination.items


def create_log_excel(mid):
    header = ['ID', 'title', 'info', 'create_time', 'creator_id']
    ret = []
    for page in range(1000):
        pagination = FAdminLog.query(mid, page, 20)
        for item in pagination.items:
            ret.append([
                    item.id,
                    item.title,
                    item.info,
                    date2string(item.create_time),
                    item.creator_id
                    ])
        if not pagination.has_next:
            break

    return make_excel("log_list", header, ret)


def get_log_download(mid):
    response = create_log_excel(mid) 
    response.headers['Content-Type'] = "utf-8"
    response.headers["Cache-Control"] = "no-cache"
    response.headers["Content-Disposition"] = "attachment; filename=log%s.xlsx" % int(time.time())
    return response


def add_log(mid, title, info):
    return FAdminLog.add(mid, title, info)
