#!/usr/bin/env python
# encoding: utf-8

from tornado.web import Application
from tornado.ioloop import IOLoop
from routes.enterprise import routes
from configs.system import sysConf


if __name__ == "__main__":
    app = Application(debug=True)
    app.add_handlers(sysConf["VHOST"], routes())

    print "===> http://{0}:{1}".format(sysConf["VHOST"], sysConf["PORT"])
    app.listen(sysConf["PORT"])
    IOLoop.current().start()