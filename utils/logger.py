#!/usr/bin/env python
# encoding: utf-8

import logging
from configs.system import sysConf


# a global variable so that we can acquire filename-lineno of the caller
log = logging.getLogger()

def _init():
    fmt = '%(asctime)s %(filename)s-%(lineno)d [%(levelname)s] %(message)s'
    fmtter = logging.Formatter(fmt)
    fname  = sysConf.get('LOG_FILE', "myapp.log")
    slevel = sysConf.get('LOG_LEVEL', "info")

    if slevel == "debug":
        level = logging.DEBUG
    elif slevel == "info":
        level = logging.INFO
    elif slevel == "warn":
        level = logging.WARNING
    elif slevel == "error":
        level = logging.ERROR
    elif slevel == "critical":
        level = logging.CRITICAL
    else:
        level = logging.INFO

    fh = logging.FileHandler(fname)
    fh.setFormatter(fmtter)
    fh.setLevel(level)

    log.setLevel(level)
    log.addHandler(fh)

    log.info("==> start logging to '{0}' with level '{1}'".format(fname, slevel))
