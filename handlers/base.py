#!/usr/bin/env python
# encoding: utf-8

import json
from tornado.web import RequestHandler, HTTPError, Finish
from tornado.httpclient import HTTPClient, HTTPRequest

from utils.mrandom import Random
from utils.mcodec import Codec
from utils.mtime import Time
from configs.system import sysConf
from configs.intoyun import ityConf


class BaseHandler(RequestHandler):
    IntoYunSrvToken = dict()

    def __init__(self, application, request, **kwargs):
        super(BaseHandler, self).__init__(application, request, **kwargs)

        if sysConf["USE_REDIS"]:
            from dbs.mredis import Redis
            self.redis = Redis()

    def check_access(self):
        # print "===> check_access..."
        # if sysConf["USE_REDIS"]:
        #     self.sessid = self.get_cookie(sysConf["SESS_KEY"])
        #     if not self.sessid:
        #         self.raise_exception(401, "please login first")
        #     hashkey = sysConf["SESS_PRE"] + self.sessid
        #     self.sess = self.redis.hgetall(hashkey)
        # else:
        #     sessStr = self.get_secure_cookie(sysConf["SESS_KEY"])
        #     if not sessStr:
        #         self.raise_exception(401, "please login first")
        #     self.sess = json.loads(sessStr)

        # print "===> self.sess: ", self.sess
        # if not self.sess:
        #     self.raise_exception(401, "session expired, please relogin")
        pass

    def set_session(self, props):
        print "===> set_session..."
        if sysConf["USE_REDIS"]:
            sessid = Codec().md5(Time().time_str()+Random().rand_str(6))
            hashkey = sysConf["SESS_PRE"] + sessid
            self.redis.hmset_and_expire(hashkey, props, sysConf["COOKIE_TTL"])
            self.set_cookie(sysConf["SESS_KEY"], sessid, sysConf.get("COOKIE_DOMAIN"))
        else:
            sessStr = json.dumps(props)
            self.set_secure_cookie(sysConf["SESS_KEY"], sessStr, None,
                                   domain=sysConf.get("COOKIE_DOMAIN"))

    def clear_session(self):
        print "===> clear_session..."
        if sysConf["USE_REDIS"]:
            hashkey = sysConf["SESS_PRE"] + self.sessid
            self.redis.delete(hashkey)
            self.set_cookie(sysConf["SESS_KEY"], self.sessid, sysConf.get("COOKIE_DOMAIN"), 0)
        else:
            self.set_secure_cookie(sysConf["SESS_KEY"], "", 0,
                                   domain=sysConf.get("COOKIE_DOMAIN"))

    @classmethod
    def renew_srv_token(self):
        ts = Time().unixts_str()
        sign = Codec().md5(ts+ityConf["APP_SECRET"])
        body = {
            "appId": ityConf["APP_ID"],
            "timestamp": ts,
            "signature": sign,
        }
        req = HTTPRequest(ityConf["HOST"]+"/v1/token", 'POST', None, json.dumps(body))
        cli = HTTPClient()
        rsp = cli.fetch(req, raise_error=False)
        if rsp.error:
            print "==> acquire intoyun-srv-token error occured "
            print rsp.error
            print rsp.body
            self.raise_HTTPError(500, "EMERGENCY: can't acquire for token")
        else:
            res = json.loads(rsp.body)
            print "===> token: " + res["token"]

            res["expireAt"] -= ityConf["RENEW_GAP"]
            res["locked"] = False
            self.IntoYunSrvToken = res
            return res["token"]

    def get_srv_token(self):
        print "===> get_srv_token"
        ist = self.IntoYunSrvToken

        if not ist.get("token") and ist.get("locked"):
            print "===> no token but someone is fetching it"
            print "===> we just raise error and wait for browser to revisit"
            print "===> You can also wait asynchronous use tornado.gen.sleep()"
            print "===> but we just a little bit of lazy :)"
            self.raise_exception(400, "once more please")

        elif (not ist.get("token") or ist["expireAt"]<Time().unixts()) and not ist.get("locked"):
            print "===> token not fetched OR expired"
            ist["locked"] = True
            try:
                token = self.renew_srv_token()
            finally:
                ist["locked"] = False
            return token
        else:
            print "===> token: " + ist["token"]
            return ist["token"]

    def raise_HTTPError(self, statusCode, msg):
        raise HTTPError(statusCode, msg)

    def raise_exception(self, statusCode, msg):
        self.clear()
        self.set_status(statusCode)
        self.write(msg)
        raise Finish()
