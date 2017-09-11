#!/usr/bin/env python
# encoding: utf-8

import json
from tornado.web import RequestHandler, HTTPError, Finish
from tornado.httpclient import HTTPClient, HTTPRequest

from dbs.mredis import Redis
from utils.mrandom import Random
from utils.mcodec import Codec
from utils.mtime import Time
from configs.system import sysConf
from configs.intoyun import ityConf


class BaseHandler(RequestHandler):
    def __init__(self, application, request, **kwargs):
        super(BaseHandler, self).__init__(application, request, **kwargs)
        self.redis = Redis()

    def check_access(self):
        self.sessid = self.get_cookie(sysConf["SESS_KEY"])
        if not self.sessid:
            self.raise_exception(401, "please login first")

        hashkey = sysConf["SESS_PRE"] + self.sessid
        self.sess = self.redis.hgetall(hashkey)
        if not self.sess:
            self.raise_exception(401, "session expired, please relogin")

    def set_session(self, props):
        sessid = Codec().md5(Time().time_str()+Random().rand_str(6))
        hashkey = sysConf["SESS_PRE"] + sessid
        self.redis.hmset_and_expire(hashkey, props, sysConf["COOKIE_TTL"])
        self.set_cookie(sysConf["SESS_KEY"], sessid, sysConf.get("COOKIE_DOMAIN"))

    def clear_session(self):
        hashkey = sysConf["SESS_PRE"] + self.sessid
        self.redis.delete(hashkey)
        self.set_cookie(sysConf["SESS_KEY"], self.sessid, sysConf.get("COOKIE_DOMAIN"), 0)

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
            print "==> acquire /token error occured "
            print rsp.error
            print rsp.body
            self.raise_HTTPError(500, "EMERGENCY: can't acquire for token")
        else:
            res = json.loads(rsp.body)
            ttl = res["expireAt"]
            res["expireAt"] -= ityConf["RENEW_GAP"]
            self.redis.hmset_and_expire(ityConf["SRV_TOKEN"], res, ttl)
            print "===> token: " + res["token"]
            return res["token"]

    def get_srv_token(self):
        print "===> get_srv_token"
        res = self.redis.hgetall(ityConf["SRV_TOKEN"])
        if not res:
            print "===> no token in redis"
            return self.renew_srv_token()
        elif int(res["expireAt"])<Time().unixts() and not res.get("locked"):
            print "===> token expired"
            self.redis.hset(ityConf["SRV_TOKEN"], "locked", "1")
            token = self.renew_srv_token()
            self.redis.hdel(ityConf["SRV_TOKEN"], "locked")
            return token
        else:
            print "===> token: " + res["token"]
            return res["token"]

    def raise_HTTPError(self, statusCode, msg):
        raise HTTPError(statusCode, msg)

    def raise_exception(self, statusCode, msg):
        self.clear()
        self.set_status(statusCode)
        self.write(msg)
        raise Finish()
