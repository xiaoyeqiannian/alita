import hashlib
from qiniu import Auth
from qiniu import put_file, put_data
from qiniu import BucketManager
from flask import current_app

def qiniu_token(key):
    try:
        q = Auth(current_app.config.get('QINIU_ACCESS_KEY'), current_app.config.get('QINIU_SECRET_KEY'))
        token = q.upload_token(current_app.config.get('QINIU_BUCKET_NAME'), key)
        return token
    except:
        return ''

def storage_save(data, mimetype='image/png', prefix=''):
    """
    七牛云存储上传文件接口
    """
    if not data:
        return None
    try:
        if not prefix:
            hash = '/%s' % (current_app.config.get('QINIU_BUCKET_NAME'))
        else:
            hash = '/%s/%s' % (current_app.config.get('QINIU_BUCKET_NAME'), prefix)
    except:
        return None

    md5str = hashlib.md5(data).hexdigest()

    key = '%s/%s' % (hash,md5str)

    try:
        q = Auth(current_app.config.get('QINIU_ACCESS_KEY'), current_app.config.get('QINIU_SECRET_KEY'))

        token = q.upload_token(current_app.config.get('QINIU_BUCKET_NAME'), key)

        ret, info = put_data(token, key, data, mime_type=mimetype, check_crc=True)
        if info and info.status_code != 200:
            return None

        if ret['key'] != key:
            return None
    except:
        return None

    return key

def storage_delete(merid, shopkey, filename):
    """七牛云存储删除文件接口
    """
    if not filename:
       return False

    try:
        q = Auth(current_app.config.get('QINIU_ACCESS_KEY'), current_app.config.get('QINIU_SECRET_KEY'))

        bucket = BucketManager(q)

        ret, info = bucket.stat(current_app.config.get('QINIU_BUCKET_NAME'), filename)
        if info and info.status_code != 200:
            return False

        if not ret or not ret['hash']:
            return True

        ret, info = bucket.delete(current_app.config.get('QINIU_BUCKET_NAME'), filename)
        if info and info.status_code != 200:
            return False
    except:
        return False

    return True


def url2qiniu(url):
    key = hashlib.md5(url).hexdigest()
    try:
        q = Auth(current_app.config.get('QINIU_ACCESS_KEY'), current_app.config.get('QINIU_SECRET_KEY'))
        bucket = BucketManager(q)
        isok = bucket.fetch(url, current_app.config.get('QINIU_BUCKET_NAME'), key)
    except:
        return None

    return "%s%s" % (current_app.config.get('QINIU_HOST'), key)

def parse_qiniu_url(url):
    key = hashlib.md5(url).hexdigest()
    return "%s%s" % (current_app.config.get('QINIU_HOST'), key)
    
