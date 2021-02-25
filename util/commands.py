import os
import sys
import importlib
import flask_script

from util.consts import *

class InitApp(flask_script.Command):

    def run(self):
        from app.account.proc import modify_user, modify_group, modify_role
        from app.account.models import User
        # 总部同样拥有创建子账号的能力
        isok, group = modify_group(
                                                group_id = GROUP_SYS_ADMIN_ID,
                                                name = "总部",
                                                kind = GROUP_KIND_GROUP)
        if not isok:
            print('初始化总部组织异常！！！')
            return
        
        print('初始化总部组织成功', group.id)
        # 生成管理员默认角色,不归属任何组织，新注册用户关联
        isok, r = modify_role(ROLE_ROOT_ID, GROUP_SYS_ADMIN_ID, name="root",
                                menu="page1,page2,page3,page4",
                                permissions=[])
        isok, r = modify_role(ROLE_ADMIN_ID, GROUP_SYS_ADMIN_ID, name="admin",
                                menu="page1,page2,page3",
                                permissions=[{"path": "/account/role/list", "method": "get"},
                                            {"path": "/account/role/modify", "method": "post"},
                                            {"path": "/account/del", "method": "post"},
                                            {"path": "/account/sub/add", "method": "post"},
                                            {"path": "/account/group/list", "method": "get"},
                                            {"path": "/account/group/modify", "method": "post"},
                                            {"path": "/account/role/del", "method": "post"},
                                            {"path": "/account/list", "method": "get"},
                                            {"path": "/account/del", "method": "post"}])
        if not isok:
            print('初始化角色异常 ！！')
            return

        # root无需关联role，拥有所有权限
        u = User.get(1)
        isok, u = modify_user(u and u.id, username="root", password="123456", group_id=group.id)
        return True