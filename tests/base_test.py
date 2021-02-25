import os
import sys
import json
import base64
import unittest
import requests
from urllib.parse import urljoin

HOME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(HOME)
from inc.retcode import RETCODE

token = None

class BaseTest(unittest.TestCase):

    test_user_name = "test"
    test_password = "123456"
    test_email = "test@test"
    test_new_password = "123456!"
    HOST = "http://127.0.0.1:5000"
    
    group_id = -1

    @classmethod
    def setUpClass(self):
        print('execute', sys._getframe().f_code.co_name)
       
    @classmethod
    def tearDownClass(self):
        print('execute', sys._getframe().f_code.co_name)

    def setUp(self):
        print('execute', sys._getframe().f_code.co_name)
        global token
        for i in range(2):
            if not token:
                self.login_user()
            if not token:
                ret = self.post("/account/regist", {"name": self.test_user_name,
                                            "password": (base64.b64encode(self.test_password.encode("utf8"))).decode('utf8')})
                self.assertEqual(ret['code'], RETCODE.OK)
        if not token:
            assert "登陆失败"

    def token_decode(self, token):
        _, info, _ = token.split('.')
        info = base64.b64decode(info + '='*3).decode("utf-8")
        print(info)
        return json.loads(info)['identity']


    def login_root(self):
        global token
        ret = self.post('/account/login', {"name": "root",
                                   "password": (base64.b64encode("123456".encode("utf8"))).decode('utf8')})
        if ret['code'] == RETCODE.OK:
            token = ret['data']['token']
            user_info = self.token_decode(token)
            BaseTest.group_id = user_info.get('group_id')
            print('get user info:', user_info)


    def login_user(self):
        global token
        ret = self.post('/account/login', {"name": self.test_user_name,
                                   "password": (base64.b64encode(self.test_password.encode("utf8"))).decode('utf8')})
        if ret['code'] == RETCODE.OK:
            token = ret['data']['token']
            user_info = self.token_decode(token)
            BaseTest.group_id = user_info.get('group_id')
            print('get user info:', user_info)


    def tearDown(self):
        print('execute', sys._getframe().f_code.co_name)


    def get(self, url, params):
        global token
        ret = requests.get( urljoin(self.HOST, url),
                            params=params,
                            timeout=10,
                            verify=False,
                            headers={"Authorization": "jwt "+(token or '')})
        print(url,'>>>', params,'<<<',ret.text)
        ret = json.loads(ret.text)
        return ret


    def post(self, url, params):
        global token
        ret = requests.post(urljoin(self.HOST, url),
                            json=params,
                            timeout=10,
                            verify=False,
                            headers={"Authorization": "jwt "+(token or '')})
        print(url,'>>>', params,'<<<',ret.text)
        ret = json.loads(ret.text)
        return ret