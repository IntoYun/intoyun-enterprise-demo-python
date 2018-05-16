#!/usr/bin/env python
# encoding: utf-8

import tornado.gen as gen
from base import BaseHandler
from utils.client import Httpc
from utils.mcodec import Codec


class SensordataHandler(BaseHandler):
    def __init__(self, application, request, **kwargs):
        super(SensordataHandler, self).__init__(application, request, **kwargs)
        self.RSC_PATH = "/v1/sensordata/"

    @gen.coroutine
    def get(self, *args, **kwargs):
        self.check_access()

        productId = self.get_query_argument("productId")
        start = self.get_query_argument("start")
        end = self.get_query_argument("end")
        path = self.RSC_PATH + "?productId=" + productId + "&start=" + start + "&end=" + end

        deviceId = self.get_query_argument("deviceId", None)
        if deviceId:
            path += "&deviceId=" + deviceId
            dpId = self.get_query_argument("dpId", None)
            if dpId:
                path += "&dpId=" + dpId

        interval = self.get_query_argument("interval", None)
        if interval:
            path += "&interval=" + interval

        futureRsp = Httpc.fetchAsync(path, "GET")
        yield futureRsp
        code, body = futureRsp.result()
        if code < 400:
            self.write(body)
            self.finish()
        else:
            err = Codec.decJson(body)
            self.raise_exception(code, str(err["code"])+": "+err["msg"])
