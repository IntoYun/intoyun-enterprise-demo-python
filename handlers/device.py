#!/usr/bin/env python
# encoding: utf-8

import tornado.gen as gen
from base import BaseHandler
from utils.client import Httpc
from utils.mcodec import Codec


class DeviceHandler(BaseHandler):
    def __init__(self, application, request, **kwargs):
        super(DeviceHandler, self).__init__(application, request, **kwargs)
        self.RSC_PATH = "/v1/device/"

    @gen.coroutine
    def get(self, *args, **kwargs):
        self.check_access()

        productId = self.get_query_argument("productId")
        path = self.RSC_PATH + "?productId=" + productId
        futureRsp = Httpc.fetchAsync(path, "GET")
        yield futureRsp
        code, body = futureRsp.result()
        if code < 400:
            self.write(body)
            self.finish()
        else:
            err = Codec.decJson(body)
            self.raise_exception(code, str(err["code"])+": "+err["msg"])
