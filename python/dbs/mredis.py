#!/usr/bin/env python
# encoding: utf-8

import redis
from configs.redis import config


class Redis(object):
    def __init__(self):
        self.client = redis.StrictRedis(
            host=config["HOST"],
            port=config["PORT"],
            db=config["DB"],
        )

    def hset(self, key, field, val):
        return self.client.hset(key, field, val)

    def hget(self, key, field):
        return self.client.hget(key)

    def hmset(self, key, props):
        return self.client.hmset(key, props)

    def hmset_and_expire(self, key, props, ttl):
        self.client.hmset(key, props)
        return self.client.expire(key, ttl)

    def hgetall(self, key):
        return self.client.hgetall(key)

    def delete(self, key):
        return self.client.delete(key)

    def expire(self, key, ttl):
        return self.client.expire(key, ttl)
