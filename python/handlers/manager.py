#!/usr/bin/env python
# encoding: utf-8

from base import BaseHandler
from utils.mtime import Time
from configs.system import sysConf


class ManagerHandler(BaseHandler):
    def __init__(self, application, request, **kwargs):
        super(ManagerHandler, self).__init__(application, request, **kwargs)
        self.managers = { "admin": "admin", "guest": "guest" }

    def get(self):
        self.check_access()
        self.write("Hello, {}!\n".format(self.sess["username"]))
        self.write("you last login at {}, ".format(self.sess["loginAt"]))
        remains = int(self.sess["unixts"]) + sysConf["COOKIE_TTL"] - Time().unixts()
        self.write("and {} seconds later will quit automatically.\n".format(remains))
        self.write("Thank you.".format(self.sess["loginAt"]))

    def post(self):
        username = self.get_body_argument("username")
        password = self.get_body_argument("password")
        secret   = self.managers.get(username)

        if not secret:
            self.raise_exception(400, "bad username")
        elif secret != password:
            self.raise_exception(400, "bad password")
        else:
            props = {
                "username": username,
                "unixts": Time().unixts_str(),
                "loginAt": Time().datetime(),
            }
            self.set_session(props)
            self.write("Hello, {}!".format(username))

