#!/usr/bin/env python
# encoding: utf-8

from tornado.gen import coroutine
from tornado.web import Application
from tornado.ioloop import IOLoop
from routes.enterprise import routes
from dbs.mkafka import Kafka
from utils.logger import log
from configs.system import sysConf

@coroutine
def fetchKafkaData():
    yield Kafka().consume()


if __name__ == "__main__":

    app = Application(debug=True, cookie_secret=sysConf["COOKIE_SECRET"])
    app.add_handlers(sysConf["VHOST"], routes())
    app.listen(sysConf["PORT"])
    log.info("==> http://{0}:{1}".format(sysConf["VHOST"], sysConf["PORT"]))

    IOLoop.current().spawn_callback(fetchKafkaData)
    IOLoop.current().start()