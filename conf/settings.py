# -*- coding:utf-8 -*-
STATIC_URL = '/static'

MONGO_REPLICA_SET = {
    'PRIMARY': ('172.100.102.163', '27019'),
    'SECONDARY': [
        ('172.100.102.163', '27018'),
        ],
    'ARBITER': ('172.100.102.163', '27017'),
    'SET_NAME': 'qfpay',
}


class MongoConf:
    host = '172.100.102.163'
    port = 27018

SERVER_HOT = True


class redis_conf:
    host = '172.100.102.101'
    port = 6379
    db = 8

REDIS_AUCTION_PREFIX = 'AUCTION_ITEM:%s'
SESSION_PREFIX = 'AUCTION_SESSION:%s'

COOKIE_DOMAIN = '/'
