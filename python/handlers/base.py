#!/usr/bin/env python
# encoding: utf-8

from tornado.web import RequestHandler, HTTPError, Finish
from dbs.mredis import Redis
from utils.mrandom import Random
from utils.mcodec import Codec
from utils.mtime import Time
from configs.system import sysConf


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

    def raise_HTTPError(self, statusCode, msg):
        raise HTTPError(statusCode, msg)

    def raise_exception(self, statusCode, msg):
        self.clear()
        self.set_status(statusCode)
        self.write(msg)
        raise Finish()
