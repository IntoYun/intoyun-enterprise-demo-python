#!/usr/bin/env python
# encoding: utf-8

import hashlib
import base64


class Codec(object):
    def md5(self, data):
        return hashlib.md5(data).hexdigest()

    def encodeBase64(self, data):
        return base64.b64encode(data)
