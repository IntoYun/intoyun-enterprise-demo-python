#!/usr/bin/env python
# encoding: utf-8

sysConf = {
    "VHOST": "YOUR_DOMAIN_NAME",
    "PORT": 8080,

    "USE_REDIS": False,
    "SESS_KEY": "mySess",
    "SESS_PRE": "web:sess:",

    "COOKIE_SECRET": "this_is_just_a_bad_secret",
    "COOKIE_DOMAIN": "YOUR_DOMAIN_NAME",
    "COOKIE_TTL": 30*60, # seconds

    "LOG_LEVEL": "YOUR_LOG_LEVEL",
    "LOG_FILE": "YOUR_LOG_FILE",
}
