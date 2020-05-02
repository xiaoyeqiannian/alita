import os
import sys
import importlib
import flask_script

class InitApp(flask_script.Command):

    def run(self):
        from app.admin.proce import modify_manager, regist_manager, modify_role, modify_permission, get_manager_by_name

        m = get_manager_by_name('superadmin')
        if not m:
            m = regist_manager('superadmin', '123456')
            print(m)

        pids = []
        isok, p = modify_permission(None, name='user manager', method='get,post', uri='user')
        if isok:
            pids.append(p.id)
        isok, p = modify_permission(None, name='log manager', method='get,post', uri='log')
        if isok:
            pids.append(p.id)
        isok, p = modify_permission(None, name='role manager', method='get,post', uri='role')
        if isok:
            pids.append(p.id)
        isok, p = modify_permission(None, name='permission manager', method='get,post', uri='permission')
        if isok:
            pids.append(p.id)

        isok, r = modify_role(None, en_name='superadmin', name='superadmin', description=None, routes=None, permissions=None)
        print(r)
        if isok:
            modify_manager(m.id, state=1, role_id=r.id)
        else:
            print('edit role error')
        return True
