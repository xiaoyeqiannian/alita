import requests
import json
from flask_sqlalchemy import Pagination

class WeChatOAuth(object):
    """
    微信auth接口
    https://developers.weixin.qq.com/miniprogram/dev/api-backend/open-api/access-token/auth.getAccessToken.html
    """
    @classmethod
    def get_access_token(cls, appid, appsecret):
        url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s'
        url = url % (appid, appsecret)
        response = requests.get(url)
        results = json.loads(response.text)
        return results


class WeChatCloudDB(object):
    """
    微信小程序云开发相关接口
    https://developers.weixin.qq.com/miniprogram/dev/wxcloud/reference-http-api/
    """
    def __init__(self, env, access_token):
        self.env = env
        self.access_token = "access_token=" + access_token
        self.query = ''
        self.url = ''
        self.method = ''

    def paginate(self, page=None, per_page=None, max_per_page=100):
        if page is None:
            page = 1

        if per_page is None:
            per_page = 20

        if max_per_page is not None:
            per_page = min(per_page, max_per_page)

        if page < 1:
            page = 1

        if per_page < 0:
            per_page = 20

        self.query += '.limit({0}).skip({1})'.format(per_page, (page-1)*per_page)
        items = self.commit()
        return Pagination(self, page, per_page, self.total, items)

    def commit(self):
        url = self.url + '?' + self.access_token
        data = {'env': self.env, 'query': self.query+'.get()' if self.method=='get' else self.query}
        response = requests.post(url, data=json.dumps(data))
        results = json.loads(response.text)
        if results and results.get('errcode')==0:
            pager = results.get('pager')
            if pager:
                self.total = pager.get('Total')
            if results.get('data'):
                return results.get('data')
            if results.get('modified'):
                return results.get('modified')
            if results.get('deleted'):
                return results.get('deleted')
            if results.get('count'):
                return results.get('count')
            if results.get('id_list'):
                return results.get('id_list')
            
        else:
            print(results.get('errcode'), results.get('errmsg'))
            return []
        
    def get(self, table, _id, **kwargs):
        self.method = 'get'
        self.url = 'https://api.weixin.qq.com/tcb/databasequery'
        self.query = 'db.collection("{}")'.format(table)
        if _id:
            self.query += '.doc("{}")'.format(_id)
        elif kwargs:
            filter_str = ''
            for k,v in kwargs.items():
                if isinstance(v, str):
                    filter_str += '{0}:"{1}"'.format(k, v)
                elif isinstance(v, bool):
                    filter_str += '{0}:{1}'.format(k, v and 'true' or 'false')
                else:
                    filter_str += '{0}:{1}'.format(k, v)

            self.query += '.where({%s})' % filter_str
        return self
   
    def update_one(self, table, _id, **kwargs):
        self.method = 'update'
        self.url = 'https://api.weixin.qq.com/tcb/databaseupdate'
        self.query = 'db.collection("{0}").doc("{1}")'.format(table, _id)
        if kwargs:
            filter_list = []
            for k,v in kwargs.items():
                if isinstance(v, str):
                    filter_list.append('{0}:"{1}"'.format(k, v))
                elif isinstance(v, bool):
                    filter_list.append('{0}:{1}'.format(k, v and 'true' or 'false'))
                else:
                    filter_list.append('{0}:{1}'.format(k, v))
            filter_str = ','.join(filter_list)
            self.query += '.update({data:{%s}})' % filter_str
        return self
    
    def delete_one(self, table, _id):
        self.method = 'delete'
        self.url = 'https://api.weixin.qq.com/tcb/databasedelete'
        self.query = 'db.collection("{0}").doc("{1}").remove()'.format(table, _id)
        return self

    def add_one(self, table, **kwargs):
        self.method = 'add'
        self.url = 'https://api.weixin.qq.com/tcb/databaseadd'
        self.query = 'db.collection("{}")'.format(table)
        if kwargs:
            filter_list = []
            for k,v in kwargs.items():
                if isinstance(v, str):
                    filter_list.append('{0}:"{1}"'.format(k, v))
                elif isinstance(v, bool):
                    filter_list.append('{0}:{1}'.format(k, v and 'true' or 'false'))
                else:
                    filter_list.append('{0}:{1}'.format(k, v))
            filter_str = ','.join(filter_list)
            self.query += '.add({data:[{%s}]})' % filter_str
        return self 
    
    def count(self, table, **kwargs):
        self.method = 'count'
        self.url = 'https://api.weixin.qq.com/tcb/databasecount'
        self.query = 'db.collection("{}")'.format(table)
        if kwargs:
            filter_str = ''
            for k,v in kwargs.items():
                if isinstance(v, str):
                    filter_str += '{0}:"{1}"'.format(k, v)
                elif isinstance(v, bool):
                    filter_str += '{0}:{1}'.format(k, v and 'true' or 'false')
                else:
                    filter_str += '{0}:{1}'.format(k, v)

            self.query += '.where({%s})' % filter_str
        self.query += '.count()' 
        return self


class WeChatCloudFile(object):
    @classmethod
    def db_file_upload(cls, access_token, env, path):
        url = 'https://api.weixin.qq.com/tcb/uploadfile'
        url = url % access_token
        data = {'env': env, 'path': path}
        response = requests.post(url, data=json.dumps(data))
        results = json.loads(response.text)
        return results
        
    @classmethod
    def db_file_download(cls, access_token, env, path):
        url = 'https://api.weixin.qq.com/tcb/batchdownloadfile'
        url = url % access_token
        data = {'env': env, 'path': path}
        response = requests.post(url, data=json.dumps(data))
        results = json.loads(response.text)
        return results
        
    @classmethod
    def db_file_delete(cls, access_token, env, path):
        url = 'https://api.weixin.qq.com/tcb/batchdeletefile'
        url = url % access_token
        data = {'env': env, 'path': path}
        response = requests.post(url, data=json.dumps(data))
        results = json.loads(response.text)
        return results
