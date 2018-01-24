#!/usr/bin/env python
# encoding: utf-8

import time
import datetime


class Time(object):
    def unixts(self):
        return int(time.time())

    def unixts_str(self):
        return str(int(time.time()))

    def time(self):
        return time.time()

    def time_str(self):
        return str(time.time())

    def datetime(self):
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

