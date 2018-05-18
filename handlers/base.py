#!/usr/bin/env python
# encoding: utf-8

from tornado.web import RequestHandler, HTTPError, Finish
from utils.mrandom import Random
from utils.mcodec import Codec
from utils.mtime import Time
from configs.system import sysConf
from configs.error import error


class BaseHandler(RequestHandler):

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
        #     self.sess = Codec.decJson(sessStr)

        # print "===> self.sess: ", self.sess
        # if not self.sess:
        #     self.raise_exception(401, "session expired, please relogin")
        pass

    def set_session(self, props):
        print "===> set_session..."
        if sysConf["USE_REDIS"]:
            sessid = Codec.md5(Time().time_str()+Random().rand_str(6))
            hashkey = sysConf["SESS_PRE"] + sessid
            self.redis.hmset_and_expire(hashkey, props, sysConf["COOKIE_TTL"])
            self.set_cookie(sysConf["SESS_KEY"], sessid, sysConf.get("COOKIE_DOMAIN"))
        else:
            sessStr = Codec.encJson(props)
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

    def raise_HTTPError(self, statusCode, msg):
        raise HTTPError(statusCode, msg)

    def raise_exception(self, statusCode, msg):
        self.clear()
        self.set_status(statusCode)
        self.write(msg)
        raise Finish()

    def throw_error(self, errType, errMsg):
        err = error[errType]
        self.raise_exception(err["staCode"], {"code": err["errCode"], "msg": errMsg})
