#!/usr/bin/env python
# encoding: utf-8

import tornado.gen as gen
from base import BaseHandler
from utils.client import Httpc
from utils.mcodec import Codec


class ControlHandler(BaseHandler):
    def __init__(self, application, request, **kwargs):
        super(ControlHandler, self).__init__(application, request, **kwargs)
        self.RSC_PATH = "/v1/control/"

    @gen.coroutine
    def post(self, *args, **kwargs):
        self.check_access()

        productId = self.get_query_argument("productId")
        path = self.RSC_PATH + "?productId=" + productId

        deviceId = self.get_query_argument("deviceId", None)
        if deviceId:
            path += "&deviceId=" + deviceId

        futureRsp = Httpc.fetchAsync(path, 'POST', self.request.body)
        yield futureRsp
        code, body = futureRsp.result()
        if code < 400:
            self.write(body)
            self.finish()
        else:
            err = Codec.decJson(body)
            self.raise_exception(code, str(err["code"])+": "+err["msg"])
