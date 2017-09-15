#!/usr/bin/env python
# encoding: utf-8

import json
import tornado.gen as gen
from tornado.web import asynchronous
from tornado.httpclient import AsyncHTTPClient, HTTPRequest

from base import BaseHandler
from configs.intoyun import ityConf


class ControlHandler(BaseHandler):
    def __init__(self, application, request, **kwargs):
        super(ControlHandler, self).__init__(application, request, **kwargs)
        self.RSC_PATH = "/v1/control/"

    @asynchronous
    @gen.coroutine
    def post(self, *args, **kwargs):
        self.check_access()

        productId = self.get_query_argument("productId")
        deviceId = self.get_query_argument("deviceId", None)
        headers = {ityConf["SRV_HEADER"]: self.get_srv_token()}
        path = ityConf["HOST"]+self.RSC_PATH+"?productId="+productId
        if deviceId:
            path += "&deviceId="+deviceId
        req = HTTPRequest(path, 'POST', headers, self.request.body)
        cli = AsyncHTTPClient()
        rsp = yield cli.fetch(req, None, raise_error=False)
        if rsp.error:
            print "==> fetch /control error occured "
            print rsp.error
            print rsp.body
            err = json.loads(rsp.body)
            self.raise_exception(500, err["msg"]+err["data"])
        else:
            self.write(rsp.body)
            self.finish()

