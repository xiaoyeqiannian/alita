import os
import sys
import json
import unittest

from alita_test import AlitaTest

HOME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(HOME)
from inc.retcode import RETCODE

class TestAccount(AlitaTest):

    def test_organization(self):
        print('----------', sys._getframe().f_code.co_name)
        organization_checked = False
        ret = self.post("/account/organization/modify", {"name": "Test1", "kind": 2})
        self.assertEqual(ret['code'], RETCODE.OK)

        self.login_root()
        ret = self.get("/account/organization/list", {})
        self.assertEqual(ret['code'], RETCODE.OK)
        self.assertTrue(len(ret['data']['items']) > 0)
        self.login_user()
        for item in ret['data']['items']:
            if int(TestAccount.organization_bid) == int(item.get('bid')):
                self.assertEqual(item.get('name'), "Test1")
                self.assertEqual(item.get('kind'), 2)
                organization_checked = True
                break
        self.assertTrue(organization_checked)
    
    def test_role(self):
        print('----------', sys._getframe().f_code.co_name)
        role_modified = False
        for i in range(2):
            ret = self.post("/account/role/modify", {"name": "test", "menu": "page1,page2", "permissions": {}})
            if ret['code'] == RETCODE.OK:
                role_modified = True
                break

            ret = self.get("/account/role/list", {"page": 1, "per_page": 1000})
            self.assertEqual(ret['code'], RETCODE.OK)
            self.assertTrue(len(ret['data']['items']) > 0)
            for item in ret['data']['items']:
                if item.get('name') == "test":
                    ret = self.post("/account/role/del", {"id": item.get('id')})
                    self.assertEqual(ret['code'], RETCODE.OK)
        self.assertTrue(role_modified)
            

    def test_add_sub_account(self):
        print('----------', sys._getframe().f_code.co_name)
        ret = self.get("/account/role/list", {})
        self.assertEqual(ret['code'], RETCODE.OK)

        role_id = ret['data']['items'][0]['id']# 随便取一个角色ID即可
        sub_account_added = False
        for i in range(2):
            ret = self.post("/account/sub/add", {"username": "sub_account", "password": self.test_password, "role_id": role_id})
            if ret['code'] == RETCODE.OK:
                sub_account_added = True
                break

            self.login_root()
            ret = self.get("/account/list", {})
            self.assertEqual(ret['code'], RETCODE.OK)
            self.assertTrue(len(ret['data']['items']) > 0)
            self.login_user()
            for item in ret['data']['items']:
                if item.get('username') == "sub_account":
                    ret = self.post("/account/del", {"bids": [item.get('bid')]})
                    self.assertEqual(ret['code'], RETCODE.OK)
        self.assertTrue(sub_account_added)
    
    def test_password_modify(self):
        print('----------', sys._getframe().f_code.co_name)
        ret = self.post("/account/password/modify", {"password": self.test_password, "new_password": self.test_new_password})
        self.assertEqual(ret['code'], RETCODE.OK)
        ret = self.post("/account/password/modify", {"password": self.test_new_password, "new_password": self.test_password})
        self.assertEqual(ret['code'], RETCODE.OK)

    def test_user_modify(self):# TODO user_bid 没有更新过来
        print('----------', sys._getframe().f_code.co_name)
        ret = self.post("/account/modify", {"bid": TestAccount.user_bid, "email": self.test_email, "name": "test2"})
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
        ret = self.post("/account/password/forget", {"username":self.test_password, "email":self.test_email})
        self.assertEqual(ret['code'], RETCODE.OK)
        ret = self.post("/account/code/verify", {"email":self.test_email, "code":"666888", "password": self.test_new_password})
        self.assertEqual(ret['code'], RETCODE.OK)
        ret = self.post('/account/login', {"username": self.test_user_name, "password": self.test_new_password})
        self.assertEqual(ret['code'], RETCODE.OK)
        ret = self.post("/account/password/modify", {"password": self.test_new_password, "new_password": self.test_password})
        self.assertEqual(ret['code'], RETCODE.OK)
        ret = self.post('/account/login', {"username": self.test_user_name, "password": self.test_password})
        self.assertEqual(ret['code'], RETCODE.OK)


if __name__ == '__main__':
    suite = unittest.TestSuite()

    suite.addTest(TestAccount("test_user_modify"))
    suite.addTest(TestAccount("test_organization"))
    suite.addTest(TestAccount("test_role"))
    suite.addTest(TestAccount("test_add_sub_account"))
    suite.addTest(TestAccount("test_password_modify"))
    suite.addTest(TestAccount("test_forget_password"))

    suite.addTest(TestAccount("test_user_permission"))
    runner = unittest.TextTestRunner()
    runner.run(suite)