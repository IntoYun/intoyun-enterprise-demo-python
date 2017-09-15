#!/usr/bin/env python
# encoding: utf-8

from handlers.manager import ManagerHandler
from handlers.product import ProductHandler
from handlers.device import DeviceHandler
from handlers.control import ControlHandler
from handlers.sensordata import SensordataHandler
from handlers.websocket import WebsocketHandler


def routes():
    return [
        (r"/websocket", WebsocketHandler),
        (r"/manager", ManagerHandler),
        (r"/product/?(?P<prdId>\w{16})?", ProductHandler),
        (r"/device", DeviceHandler),
        (r"/control", ControlHandler),
        (r"/sensordata", SensordataHandler),
    ]