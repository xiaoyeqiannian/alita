import os
import sys
import json
import base64
import unittest
import requests

HOME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(HOME)
from inc.retcode import RETCODE

token = None

class AlitaTest(unittest.TestCase):

    test_user_name = "test"
    test_password = "test"
    test_email = "test@test"
    test_new_password = "123456"
    HOST = "http://127.0.0.1:5000"
    
    organization_bid = 0
    user_bid = 0
    @classmethod
    def setUpClass(self):
        print('execute', sys._getframe().f_code.co_name)
       
    @classmethod
    def tearDownClass(self):
        print('execute', sys._getframe().f_code.co_name)

    def setUp(self):
        print('execute', sys._getframe().f_code.co_name)
        for i in range(2):
            if not AlitaTest.user_bid:
                self.login_user()
            if not AlitaTest.user_bid:
                ret = self.post("/account/regist", {"username": self.test_user_name, "password": self.test_password})
                self.assertEqual(ret['code'], RETCODE.OK)
        if not AlitaTest.user_bid:
            assert "登陆失败"

    def token_decode(self, token):
        _, info, _ = token.split('.')
        info = base64.b64decode(info + '='*3).decode("utf-8")
        return json.loads(info)['identity']

    def login_root(self):
        global token
        ret = self.post('/account/login', {"username": "root", "password": "123456"})
        if ret['code'] == RETCODE.OK:
            token = ret['data']['token']
            user_info = self.token_decode(token)
            AlitaTest.user_bid = user_info['user_bid']
            AlitaTest.organization_bid = user_info['organization_bid']
            print('set root bid:', AlitaTest.user_bid, AlitaTest.organization_bid)

    def login_user(self):
        global token
        ret = self.post('/account/login', {"username": self.test_user_name, "password": self.test_password})
        if ret['code'] == RETCODE.OK:
            token = ret['data']['token']
            user_info = self.token_decode(token)
            AlitaTest.user_bid = user_info['user_bid']
            AlitaTest.organization_bid = user_info['organization_bid']
            print('set user bid:', AlitaTest.user_bid, AlitaTest.organization_bid)

    def tearDown(self):
        print('execute', sys._getframe().f_code.co_name)

    def get(self, url, params):
        global token
        ret = requests.get( self.HOST + url,
                            params=params,
                            timeout=10,
                            verify=False,
                            headers={"Authorization": "jwt "+(token or '')})
        ret = json.loads(ret.text)
        print(url,'>>>', params,'<<<',ret)
        return ret

    def post(self, url, params):
        global token
        ret = requests.post(self.HOST + url,
                            json=params,
                            timeout=10,
                            verify=False,
                            headers={"Authorization": "jwt "+(token or '')})
        ret = json.loads(ret.text)
        print(url,'>>>', params,'<<<',ret)
        return ret