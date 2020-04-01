# -*- coding:utf-8 -*-
import hashlib
import binascii
import hmac

ENCRYPT_SECRET = b"alitaalitaalita"
def hmac_encrypt(password):
    """
    used to encrypt login password
    """
    if isinstance(password, str):
        password = password.encode('utf-8')
    hash = hmac.new(ENCRYPT_SECRET, password, hashlib.sha256)
    return binascii.b2a_base64(hash.digest())[:-1]
