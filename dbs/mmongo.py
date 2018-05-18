#!/usr/bin/env python
# encoding: utf-8

from tornado import gen
from motor.motor_tornado import MotorClient
from bson.objectid import ObjectId
from configs.mongo import config


class Mongo(object):
    client = MotorClient(config["HOST"], config["PORT"], connectTimeoutMS=3000)
    authedDB = dict()

    def __init__(self, coll=None, db=None):
        self.db = self.client[db or config["DB"]]
        self.coll = self.db[coll or config["COLL"]]

    @gen.coroutine
    def get_coll(self, coll=None):
        if not self.authedDB.get(self.db.name):
            print "==> authed db: ", self.db.name
            yield self.db.authenticate(config["USER"], config["PSWD"], mechanism='SCRAM-SHA-1')
            self.authedDB[self.db.name] = True

        if coll:
            raise gen.Return(self.db[coll])
        else:
            raise gen.Return(self.coll)

    @gen.coroutine
    def insert_one(self, doc, coll=None):
        mcoll = yield self.get_coll(coll)
        result = yield mcoll.insert_one(doc)
        print "==> insert_one result: ", result
        raise gen.Return(str(result.inserted_id))

    @gen.coroutine
    def insert_many(self, docs, coll=None):
        mcoll = yield self.get_coll(coll)
        result = yield mcoll.insert_many(docs)
        print "==> insert_many result: ", result
        raise gen.Return([str(id) for id in result.inserted_ids])

    @gen.coroutine
    def find_one(self, qry, rfs=None, coll=None):
        mcoll = yield self.get_coll(coll)
        if qry.get("_id"):
            qry["_id"] = ObjectId(qry["_id"])

        result = yield mcoll.find_one(qry, rfs)
        if result and result.get("_id"):
            result["_id"] = str(result["_id"])
        print "==> find_one result: ", result
        raise gen.Return(result)

    @gen.coroutine
    def find(self, qry, rfs=None, coll=None):
        mcoll = yield self.get_coll(coll)
        if qry.get("_id"):
            qry["_id"] = ObjectId(qry["_id"])
        cursor = mcoll.find(qry, rfs)

        result = []
        while (yield cursor.fetch_next):
            doc = cursor.next_object()
            if doc.get("_id"):
                doc["_id"] = str(doc["_id"])
            result.append(doc)
        print "==> find result: ", result
        raise gen.Return(result)

    @gen.coroutine
    def update_one(self, qry, doc, coll=None):
        mcoll = yield self.get_coll(coll)
        if qry.get("_id"):
            qry["_id"] = ObjectId(qry["_id"])

        result = yield mcoll.update_one(qry, {'$set': doc})
        print "==> update_one result: ", result.modified_count
        raise gen.Return(result.modified_count)

    @gen.coroutine
    def delete_one(self, qry, coll=None):
        mcoll = yield self.get_coll(coll)
        if qry.get("_id"):
            qry["_id"] = ObjectId(qry["_id"])

        result = yield mcoll.delete_one(qry)
        print "==> delete_one result: ", result.deleted_count
        raise gen.Return(result.deleted_count)
