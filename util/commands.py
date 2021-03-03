import os
import sys
import base64
import importlib
import flask_script

from util.consts import *

class InitApp(flask_script.Command):

    def run(self):
        from app.account.proc import create_user, modify_group, modify_role
        from app.account.models import User
        # 总部同样拥有创建子账号的能力
        group = modify_group(
                    group_id = GROUP_SYS_ADMIN_ID,
                    name = "总部",
                    kind = GROUP_KIND_GROUP)
        print('init group', group.id)
        # 生成管理员默认角色,不归属任何组织，新注册用户关联
        role = modify_role(
                    ROLE_ROOT_ID,
                    GROUP_SYS_ADMIN_ID,
                    name="root",
                    menu="page1,page2,page3,page4",
                    permissions=[])
        print("init root role", role)
        role = modify_role(
                    ROLE_ADMIN_ID,
                    GROUP_SYS_ADMIN_ID,
                    name="admin",
                    menu="page1,page2,page3",
                    permissions=[
                                {"path": "/account/list", "method": "get"},
                                {"path": "/account/del", "method": "post"},
                                {"path": "/account/:id/modify", "method": "post"},
                                {"path": "/account/sub/add", "method": "post"},
                                {"path": "/account/role/list", "method": "get"},
                                {"path": "/account/role/modify", "method": "post"},
                                {"path": "/account/role/del", "method": "post"},
                                {"path": "/account/group/list", "method": "get"},
                                {"path": "/account/group/:id/modify", "method": "post"},
                                ])
        print("init admin role", role)
        u = User.query.filter_by(role_id = ROLE_ROOT_ID, name = "root").first()
        if not u:
            u = create_user(
                    name = "root",
                    password = base64.b64encode("123456".encode("utf8")).decode('utf8'),
                    group_id = group.id,
                    role_id = ROLE_ROOT_ID)
        print("root user:", u)
        return True