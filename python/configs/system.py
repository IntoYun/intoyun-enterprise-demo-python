#!/usr/bin/env python
# encoding: utf-8

sysConf = {
    "VHOST": "192.168.0.46",
    "PORT": 8080,

    "USE_REDIS": False,
    "SESS_KEY": "mySess",
    "SESS_PRE": "web:sess:",

    "COOKIE_SECRET": "this_is_just_a_bad_secret",
    "COOKIE_DOMAIN": "192.168.0.46",
    "COOKIE_TTL": 30*60, # seconds
}
