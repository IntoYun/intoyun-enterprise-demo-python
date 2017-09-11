#!/usr/bin/env python
# encoding: utf-8

import json
import tornado.gen as gen
from tornado.web import asynchronous
from tornado.httpclient import AsyncHTTPClient, HTTPRequest

from base import BaseHandler
from configs.intoyun import ityConf


class SensordataHandler(BaseHandler):
    def __init__(self, application, request, **kwargs):
        super(SensordataHandler, self).__init__(application, request, **kwargs)
        self.RSC_PATH = "/v1/sensordata/"

    @asynchronous
    @gen.coroutine
    def get(self, *args, **kwargs):
        self.check_access()

        productId = self.get_query_argument("productId")
        start = self.get_query_argument("start")
        end = self.get_query_argument("end")
        path = ityConf["HOST"]+self.RSC_PATH+"?productId="+productId+"&start="+start+"&end="+end

        deviceId = self.get_query_argument("deviceId", None)
        if deviceId:
            path += "&deviceId="+deviceId
            dpId = self.get_query_argument("dpId", None)
            if dpId:
                path += "&dpId="+dpId

        interval = self.get_query_argument("interval", None)
        if interval:
            path += "&interval="+interval

        headers = {ityConf["SRV_HEADER"]: self.get_srv_token()}
        req = HTTPRequest(path, 'GET', headers)
        cli = AsyncHTTPClient()
        rsp = yield cli.fetch(req, None, raise_error=False)
        if rsp.error:
            print "==> fetch /sensordata error occured "
            print rsp.error
            print rsp.body
            err = json.loads(rsp.body)
            self.raise_exception(500, err["msg"]+err["data"])
        else:
            self.write(rsp.body)
            self.finish()

