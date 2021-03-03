import os
import sys
import json
import unittest

from base_test import BaseTest

HOME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(HOME)
from inc.retcode import RETCODE

class TestAccount(BaseTest):

    def test_group(self):
        print('----------', sys._getframe().f_code.co_name)
        group_checked = False
        ret = self.post(f"/account/group/{self.group_id}/modify", {"name": "Test1", "kind": 2})
        self.assertEqual(ret['code'], RETCODE.OK)

        self.login_root()
        ret = self.get("/account/group/list", {"page": 1, "per_page": 2000})
        self.assertEqual(ret['code'], RETCODE.OK)
        self.assertTrue(len(ret['data']['items']) > 0)
        self.login_user()
        for item in ret['data']['items']:
            if int(TestAccount.group_id) == int(item.get('id')):
                self.assertEqual(item.get('name'), "Test1")
                self.assertEqual(item.get('kind'), 2)
                group_checked = True
                break
        self.assertTrue(group_checked)
    
    def test_role(self):
        print('----------', sys._getframe().f_code.co_name)
        self.post("/account/role/modify", {"name": "test", "menu": "page1,page2", "permissions":[]})
        ret = self.get("/account/role/list", {"page": 1, "per_page": 1000})
        self.assertEqual(ret['code'], RETCODE.OK)
        self.assertTrue(len(ret['data']['items']) > 0)
        todel = []
        for item in ret['data']['items']:
            if item.get('name') == "test":
                todel.append(item.get('id'))
        if todel:
            ret = self.post("/account/role/del", {"ids": todel})
            self.assertEqual(ret['code'], RETCODE.OK)
            

    def test_add_sub_account(self):
        print('----------', sys._getframe().f_code.co_name)
        ret = self.get("/account/role/list", {})
        self.assertEqual(ret['code'], RETCODE.OK)
        if len(ret['data']['items']) <= 0:
            self.post("/account/role/modify", {"name": "test", "menu": "page1,page2", "permissions":[]})
            ret = self.get("/account/role/list", {})

        role_id = ret['data']['items'][0]['id']# 随便取一个角色ID即可
        ret = self.post("/account/sub/add", {"name": "sub_account",
                                            "password": self.b64_encode(self.test_password),
                                            "role_id": role_id})
        self.login_root()
        ret = self.get("/account/list", {})
        self.assertEqual(ret['code'], RETCODE.OK)
        self.assertTrue(len(ret['data']['items']) > 0)
        self.login_user()
        todel = []
        for item in ret['data']['items']:
            if item.get('name') == "sub_account":
                todel.append(item.get('id'))
        if todel:
            ret = self.post("/account/del", {"ids": todel})
            self.assertEqual(ret['code'], RETCODE.OK)
    
    def test_password_modify(self):
        print('----------', sys._getframe().f_code.co_name)
        ret = self.post("/account/password/modify",
                    {"password": self.b64_encode(self.test_password),
                    "new_password": self.b64_encode(self.test_new_password)})
        self.assertEqual(ret['code'], RETCODE.OK)
        ret = self.post("/account/password/modify", 
                    {"password": self.b64_encode(self.test_new_password),
                    "new_password": self.b64_encode(self.test_password)})
        self.assertEqual(ret['code'], RETCODE.OK)

    def test_user_modify(self):
        print('----------', sys._getframe().f_code.co_name)
        ret = self.post(f"/account/{self.user_id}/modify", {"email": self.test_email})
        self.assertEqual(ret['code'], RETCODE.OK)

    def test_user_permission(self):
        print('----------', sys._getframe().f_code.co_name)

    def test_permission(self):
        print('----------', sys._getframe().f_code.co_name)
        ret = self.get('/account/role/list', {})
        if ret['code'] != RETCODE.ROLEERR:
            # add role
            params = {  "name": "cc",
                        "menu": "page1,page2",
                        "permissions": [
                            {"path":"/role/list","method":"get"},
                            {"path":"/role/modify","method":"post"}],
                        "state": 1}
            ret = self.post('/account/role/modify', params)
            self.assertEqual(ret['code'], RETCODE.OK)
            # add permission

        ret = self.get('/account/role/list', {})
        self.assertEqual(ret['code'], RETCODE.OK)
        self.assertEqual(ret['total'], 1)
        self.assertEqual(len(ret['items']), 1)
        self.assertEqual(ret["items"][0]['name'], params['name'])
        self.assertEqual(ret["items"][0]["menu"], params['menu'])
        self.assertEqual(ret["items"][0]["permissions"], params['permissions'])

    def test_forget_password(self):
        print('----------', sys._getframe().f_code.co_name)
        ret = self.post("/account/password/forget", {"name":self.test_user_name, "email":self.test_email})
        self.assertEqual(ret['code'], RETCODE.OK)
        ret = self.post("/account/code/verify", {"name":self.test_user_name, "email":self.test_email, "code":"666888",
                                                "new_password": self.b64_encode(self.test_new_password)})
        self.assertEqual(ret['code'], RETCODE.OK)
        ret = self.post('/account/login', {"name": self.test_user_name,
                                            "password": self.b64_encode(self.test_new_password)})
        self.assertEqual(ret['code'], RETCODE.OK)
        ret = self.post("/account/password/modify", {"password": self.b64_encode(self.test_new_password),
                                                    "new_password": self.b64_encode(self.test_password)})
        self.assertEqual(ret['code'], RETCODE.OK)
        ret = self.post('/account/login', {"name": self.test_user_name, "password": self.b64_encode(self.test_password)})
        self.assertEqual(ret['code'], RETCODE.OK)


if __name__ == '__main__':
    suite = unittest.TestSuite()

    suite.addTest(TestAccount("test_user_modify"))
    suite.addTest(TestAccount("test_group"))
    suite.addTest(TestAccount("test_role"))
    suite.addTest(TestAccount("test_add_sub_account"))
    suite.addTest(TestAccount("test_password_modify"))
    suite.addTest(TestAccount("test_forget_password"))
    suite.addTest(TestAccount("test_user_permission"))
    runner = unittest.TextTestRunner()
    runner.run(suite)