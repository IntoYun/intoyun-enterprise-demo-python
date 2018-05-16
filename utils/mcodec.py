#!/usr/bin/env python
# encoding: utf-8

import json
import base64
import hashlib
import binascii
from Crypto.Cipher import AES


BS = 16 #AES_BLOCK_SIZE
pad = lambda s: s + (BS - len(s) % self.AES_BS) * chr(BS - len(s) % BS)
unpad = lambda s : s[0:-ord(s[-1])]

class Codec(object):

    @staticmethod
    def md5(data):
        return hashlib.md5(data).hexdigest()

    @staticmethod
    def encBase64(data):
        return base64.b64encode(data)

    @staticmethod
    def decBase64(data):
        return base64.b64decode(data)

    @staticmethod
    def encJson(data):
        return json.dumps(data)

    @staticmethod
    def decJson(data):
        return json.loads(data)

    @staticmethod
    def decAesCBC(data, aes_key):
        iv = data[:AES.block_size]
        cipher = AES.new(aes_key, AES.MODE_CBC, iv)

        payload = data[16:]
        return unpad(cipher.decrypt(payload))

    @staticmethod
    def encHex(data):
        return binascii.hexlify(data)

    @staticmethod
    def decHex(data):
        return binascii.unhexlify(data)
