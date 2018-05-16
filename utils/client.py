#!/usr/bin/env python
# encoding: utf-8

import tornado.gen as gen
from tornado.httpclient import HTTPClient, AsyncHTTPClient, HTTPRequest
from utils.mtime import Time
from utils.mcodec import Codec
from configs.intoyun import ityConf


class Httpc(object):
    '''
    TODO:
        1. use connection-pool
        2. make get_srv_token() asynchronous?
    '''

    IntoYunSrvToken = dict()
    expire_ahead = 5*60 # 5min

    @classmethod
    def renew_srv_token(cls):
        ts = Time().unixts_str()
        sign = Codec.md5(ts+ityConf["APP_SECRET"])
        body = {
            "appId": ityConf["APP_ID"],
            "timestamp": ts,
            "signature": sign,
        }
        req = HTTPRequest(ityConf["HOST"]+"/v1/token", 'POST', None, Codec.encJson(body))
        cli = HTTPClient()
        rsp = cli.fetch(req, raise_error=False)
        cli.close()
        if rsp.error:
            print "==> EMERGENCY: CAN'T acquire for intoyun-srv-token"
            print rsp.error
            print rsp.body
            return None
        else:
            res = Codec.decJson(rsp.body)
            res["expireAt"] -= cls.expire_ahead
            res["locked"] = False
            cls.IntoYunSrvToken = res
            print "===> renew token to: " + res["token"]
            return res["token"]

    @classmethod
    def get_srv_token(cls):
        ist = cls.IntoYunSrvToken
        if not ist.get("token") and ist.get("locked"):
            print "===> no token but someone is fetching it"
            print "===> You can wait and revisit it"
            print "===> Use tornado.gen.sleep() if fetch asynchronous"
            return None
        elif (not ist.get("token") or ist["expireAt"]<Time().unixts()) and not ist.get("locked"):
            ist["locked"] = True
            try:
                token = cls.renew_srv_token()
            finally:
                ist["locked"] = False
            return token
        else:
            return ist["token"]

    @classmethod
    @gen.coroutine
    def fetchAsync(cls, path, method, body=None):
        headers = {ityConf["SRV_HEADER"]: cls.get_srv_token()}
        path = ityConf["HOST"] + path
        req = HTTPRequest(path, method, headers, body)
        rsp = yield AsyncHTTPClient().fetch(req, None, raise_error=False)
        raise gen.Return((rsp.code, rsp.body))

    @classmethod
    def fetchSync(cls, path, method, body=None):
        headers = {ityConf["SRV_HEADER"]: cls.get_srv_token()}
        path = ityConf["HOST"] + path
        req = HTTPRequest(path, method, headers, body)
        cli = HTTPClient()
        rsp = cli.fetch(req, raise_error=False)
        cli.close()
        return (rsp.code, rsp.body)
