#!/usr/bin/env python
# encoding: utf-8

from handlers.manager import ManagerHandler
from handlers.product import ProductHandler


def routes():
    return [
        (r"/manager", ManagerHandler),
        (r"/product", ProductHandler),
    ]