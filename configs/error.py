#!/usr/bin/env python
# encoding: utf-8

error = {
    "common.badCall":    {"staCode": 405, "errCode": 40001},
    "common.badParam":   {"staCode": 400, "errCode": 40002},
    "common.forbidden":  {"staCode": 403, "errCode": 40003},
    "common.notFound":   {"staCode": 400, "errCode": 40004},
    "common.badPayload": {"staCode": 400, "errCode": 40005},

    "manager.badParam":   {"staCode": 400, "errCode": 40102},
    "manager.forbidden":  {"staCode": 403, "errCode": 40103},
    "manager.notFound":   {"staCode": 400, "errCode": 40104},
    "manager.badPayload": {"staCode": 400, "errCode": 40105},
}
