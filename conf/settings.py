# -*- coding:utf-8 -*-
STATIC_URL = '/auction/static'
# STATIC_URL = '/static'

MONGO_REPLICA_SET = {
    'PRIMARY': ('172.100.102.163', '27019'),
    'SECONDARY': [
        ('172.100.102.163', '27018'),
        ],
    'ARBITER': ('172.100.102.163', '27017'),
    'SET_NAME': 'qfpay',
}


class MongoConf:
    host = '127.0.0.1'
    port = 27011

SERVER_HOT = True


class redis_conf:
    host = '127.0.0.1'
    port = 6379
    db = 8

REDIS_AUCTION_PREFIX = 'AUCTION_ITEM:%s'
REDIS_PV_PREFIX = 'AUCTION_PV:%s'
SESSION_PREFIX = 'AUCTION_SESSION:%s'

COOKIE_DOMAIN = '/'
