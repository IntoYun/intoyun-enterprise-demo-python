#!/usr/bin/env python
# encoding: utf-8

from pymongo import MongoClient
from configs.mongo import config


class Mongo(object):
    def __init__(self):
        self.client = MongoClient(config["HOST"], config["PORT"])
        self.db = self.client[config["DB"]]
        self.coll = self.db[config["COLL"]]

    def insert(self, doc, coll=None):
        Coll = coll and self.db[coll] or self.coll
        Coll.insert(doc)

    def find_one(self, qry, rfs=None):
        Coll = coll and self.db[coll] or self.coll
        Coll.find_one(qry, rfs)

    def find(self, qry, rfs=None):
        Coll = coll and self.db[coll] or self.coll
        Coll.find(qry, rfs)

