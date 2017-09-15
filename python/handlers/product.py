#!/usr/bin/env python
# encoding: utf-8

import json
import tornado.gen as gen
from tornado.web import asynchronous
from tornado.httpclient import AsyncHTTPClient, HTTPRequest

from base import BaseHandler
from configs.intoyun import ityConf


class ProductHandler(BaseHandler):
    def __init__(self, application, request, **kwargs):
        super(ProductHandler, self).__init__(application, request, **kwargs)
        self.RSC_PATH = "/v1/product/"

    @asynchronous
    @gen.coroutine
    def get(self, *args, **kwargs):
        self.check_access()

        headers = {ityConf["SRV_HEADER"]: self.get_srv_token()}
        path = ityConf["HOST"]+self.RSC_PATH+(kwargs["prdId"] or "")
        req = HTTPRequest(path, 'GET', headers)
        cli = AsyncHTTPClient()
        rsp = yield cli.fetch(req, None, raise_error=False)
        if rsp.error:
            print "==> fetch /product error occured "
            print rsp.error
            print rsp.body
            err = json.loads(rsp.body)
            self.raise_exception(err["code"], err["msg"])
        else:
            self.write(rsp.body)
            self.finish()

