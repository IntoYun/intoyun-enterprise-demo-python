#!/usr/bin/env python
# encoding: utf-8

import tornado.escape
import tornado.websocket

class WebsocketHandler(tornado.websocket.WebSocketHandler):
    trusted = dict()
    anonymous = set()

    def __init__(self, application, request, **kwargs):
        super(WebsocketHandler, self).__init__(application, request, **kwargs)
        self.deviceId = None

    def get_compression_options(self):
        # Non-None enables compression with default options.
        return {}

    def open(self):
        self.add_anonymous(self)

    def on_close(self):
        if self.deviceId:
            self.del_trusted(self.deviceId, self)
        else:
            self.remove_anonymous(self)

    def on_message(self, message):
        print "=====> WebSocket receive: " + message

    @classmethod
    def add_anonymous(cls, conn):
        #TODO: need close later if not auth
        # we can use IOLoop.callback()
        cls.anonymous.add(conn)

    @classmethod
    def remove_anonymous(cls, conn):
        cls.anonymous.remove(conn)

    @classmethod
    def add_trusted(cls, did, conn):
        if cls.trusted.get(did):
            cls.trusted[did].add(conn)
        else:
            cls.trusted[did] = set()
            cls.trusted[did].add(conn)
        cls.anonymous.remove(conn)

    @classmethod
    def del_trusted(cls, did, conn):
        if len(cls.trusted.get(did))==1:
            del cls.trusted[did]
        else:
            cls.trusted[did].remove(conn)
