#-*- coding:utf-8 -*-
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import web, time
import pymongo
from conf.settings import STATIC_URL, MONGO_REPLICA_SET, SERVER_HOT, redis_conf, REDIS_AUCTION_PREFIX, \
    SESSION_PREFIX, COOKIE_DOMAIN, MongoConf, REDIS_PV_PREFIX
from logger import initlog
import types
from response.resp import success, error, QFRET
import redis
from util.redis_helper import RedisString
from bson import ObjectId
import datetime
import hashlib
import uuid

ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OPENAPI_PATH = os.path.dirname(ROOT_PATH)
GRAY_VERSION = os.path.basename(ROOT_PATH)
log = initlog({
    'INFO': '%s/log/auction_%s.log' % (OPENAPI_PATH, GRAY_VERSION),
    'NOTE': '%s/log/auction_%s.log' % (OPENAPI_PATH, GRAY_VERSION),
    'WARN': '%s/log/auction_%s.log' % (OPENAPI_PATH, GRAY_VERSION),
    'ERROR': '%s/log/auction_%s.log' % (OPENAPI_PATH, GRAY_VERSION),
    'MPAY': '%s/log/auction_pay_%s.log' % (OPENAPI_PATH, GRAY_VERSION)
}, backup_count=0, console=True)

urls = (
    '/auction/ping', 'Ping',
    '/auction/item/(.+)', 'Item',
    '/auction/auction', 'Auction',
    '/auction/reg', 'Register',
    '/auction/login', 'Login',
    '/auction/iwant', 'Iwant',
    '/auction/statistics', 'Statistics',
)


global_args = {
    'static': STATIC_URL,
}


def get_replica_set_client():
    rs_client = pymongo.MongoClient(host=MongoConf.host, port=MongoConf.port)
    # seeds = [conf['PRIMARY']] + conf['SECONDARY']
    # rs_client = pymongo.MongoReplicaSetClient(','.join([':'.join(addr) for addr in seeds]),
    #                                           document_class=dict,
    #                                           replicaSet=conf['SET_NAME'],
    #                                           use_greenlets=True,
    #                                           secondary_acceptable_latency_ms=100,
    #                                           read_preference=pymongo.ReadPreference.SECONDARY_PREFERRED)
    return rs_client


mongo_client = get_replica_set_client()
mongo_auction = mongo_client.auction
redis_client = redis.Redis(host=redis_conf.host, port=redis_conf.port, db=redis_conf.db)

render = web.template.render(os.path.dirname(os.path.abspath(__file__)) + '/html', cache=True, globals=global_args)


def unicode2utf8(text):
    if isinstance(text, types.UnicodeType):
        return text.encode('utf-8')
    else:
        return text


def utf82unicode(text):
    if isinstance(text, types.StringType):
        return text.decode('utf-8')
    else:
        return text



class Ping:
    """
    测试
    """
    def GET(self):
        return 'OK'


class Register:
    """
    注册
    """
    def GET(self):
        return render.reg()

    def POST(self):
        data = web.input()
        email = data.get('email', '')
        passwd = data.get('passwd', '')
        nickname = data.get('nickname', '')
        if not email or not passwd or not nickname:
            return render.error('注册信息不全，请重新输入')
        hpass = hashlib.sha1(passwd).hexdigest()
        exist_user = mongo_auction.user.find_one({'$or': [{'nickname': nickname}, {'email': email}]})
        if exist_user:
            if exist_user.get('email') == email:
                return render.error('注册邮箱已存在，请重新注册')
            else:
                return render.error('注册昵称已存在，请重新注册')
        user_id = mongo_auction.user.insert(dict(
            email=email,
            nickname=nickname,
            passwd=hpass,
            created=datetime.datetime.now(),
        ))
        return login_return(str(user_id))


def login_return(user_id):
    sessionid = generate_sessionid(user_id)
    web.setcookie('sessionid', sessionid, path='/')
    cookie_redirect_url = web.cookies().get('current_page')
    redirect_url = cookie_redirect_url if cookie_redirect_url else '/auction/item/56a0dc0d35e9d494bcb25b69'
    raise web.redirect(redirect_url)


class Iwant:
    """
    我也要拍卖
    """
    def GET(self):
        return render.iwant()


class Login:
    """
    登入
    """
    def GET(self):
        return render.login()

    def POST(self):
        data = web.input()
        email = data.get('email', '')
        passwd = data.get('passwd', '')
        if not email or not passwd:
            return render.error('登入信息不全，请重新输入')
        hpass = hashlib.sha1(passwd).hexdigest()
        exist_user = mongo_auction.user.find_one({'email': email})
        if not exist_user:
            return render.error('邮箱未注册，请注册')
        if hpass != exist_user.get('passwd'):
            return render.error('密码不正确， 请重新输入')

        user_id = exist_user.get('_id')
        return login_return(user_id)


def generate_sessionid(user_id):
    sessionid = str(uuid.uuid4())
    redis_session = RedisString(SESSION_PREFIX % sessionid, redis_client)
    redis_session.set(user_id)
    return sessionid


class Item:
    """
    拍卖商品展示
    """
    def GET(self, item_id):
        if not item_id:
            return render.error('未传商品ID')
        if not len(item_id) == 24:
            return render.error('商品ID格式不正确')
        item_dict = mongo_auction.item.find_one({'_id': ObjectId(item_id)})
        if not item_dict:
            return render.error('没有找到拍卖商品')
        ritem_price = RedisString(REDIS_AUCTION_PREFIX % item_id, redis_client)
        current_price = ritem_price.get_number()
        if not current_price:
            current_price = int(item_dict.get('init_price', 10))
        item_dict['current_price'] = current_price
        ritem_price.set(current_price)

        # print item_dict
        # print type(item_dict)
        return render.item(item_dict)


def check_user(func):
    def _(self, *args, **kwargs):
        session_key = web.cookies().get('sessionid')
        if session_key:
            user_id = redis_client.get(SESSION_PREFIX % str(session_key))
            if user_id:
                self.user_id = user_id
            else:
                return error(QFRET.SESSIONERR, '未找到登入信息')
        else:
            return error(QFRET.SESSIONERR, '未找到登入信息')
        return func(self, *args, **kwargs)

    return _


class Statistics:
    """
    统计
    """
    def POST(self):
        data = web.input()
        pname = data.get('pname')
        pv_obj = RedisString(REDIS_PV_PREFIX % pname, redis_client)
        num = pv_obj.incrby()
        return success({'num': num})


class Auction:
    """
    拍价
    """
    @check_user
    def POST(self):
        data = web.input()
        item_id = data.get('item_id', '')
        add_price = int(data.get('add_price', 10))
        if not item_id:
            return error(QFRET.PARAMERR, '未传商品信息')
        ritem_price = RedisString(REDIS_AUCTION_PREFIX % item_id, redis_client)
        current_price = ritem_price.get_number()
        item_dict = mongo_auction.item.find_one({'_id': ObjectId(item_id)})
        if not current_price:
            current_price = int(item_dict.get('init_price', 10))
            ritem_price.set(current_price)
        final_price = current_price + add_price
        # Redis 计入当前累加价格
        ritem_price.incrby(add_price)
        # Mongo 记录拍卖记录
        timenow = datetime.datetime.now()
        mongo_auction.auction_record.insert(dict(
            item_id=item_dict.get('_id'),
            bidders=self.user_id,
            owner=item_dict.get('user_id'),
            price=final_price,
            created=timenow,
        ))
        ret = {'price': final_price}
        return success(ret)



def fmt_log(logstr):
    """
    日志格式化  去除换行
    :param logstr:
    :return:
    """
    if not logstr:
        return logstr
    if not isinstance(logstr, basestring):
        return logstr
    return logstr.replace('\n', ' ')


def api_log(handler):
    start_time = time.time()
    try:
        ret = handler()
    except Exception, e:
        if type(e) in (web.webapi._NotFound, web.webapi.NoMethod, web.webapi.Redirect, web.webapi.SeeOther):
            ret = ""
        else:
            buf = "发生未知异常：%s:%s, url: %s" % (Exception,e,web.ctx.path)
            log.info(buf.replace('\n', ''))
            ret = "error"

    ctx = web.ctx
    if getattr(ctx, 'path') != '/ping' and getattr(ctx, 'path') != '/favicon.ico':
        logfields = []
        ip = unicode2utf8(ctx.env.get('HTTP_X_FORWARDED_FOR', ctx.ip).split(',')[0] or ctx.get('REMOTE_ADDR'))
        logfields.append('%s=%s' % ('ip', ip))
        method = unicode2utf8(ctx['method'])
        logfields.append('%s=%s' % ('method', method))
        logfields.append('path=%s%s' % (unicode2utf8(ctx.homepath), unicode2utf8(ctx.path)))
        if 'query' in ctx:
            logfields.append('query=%s' % unicode2utf8(ctx['query'])[1:])

        if ctx.method == 'POST':
            body = []
            if web.input():
                params = web.input()
                for k, v in params.iteritems():
                    if isinstance(v, basestring):
                        if k == 'password':
                            body.append('password=%s' % ('*' * len(v)))
                        else:
                            body.append('%s=%s' % (k, unicode2utf8(v)))
                    else:
                        body.append('%s=%s' % (k, type(v)))
                data = '&'.join(body)
            else:
                data = web.data()
            try:
                logfields.append('body=%s' % data)
            except Exception, e:
                log.error(e)
                logfields.append('body=%s' % str(body))

        logfields.append('status=%s' % ctx.status.split(' ')[0])
        logfields.append('time=%.1f' % ((time.time() - start_time) * 1000))
        logfields.append('len=%d' % (len(ret) if isinstance(ret, basestring) else -1))
        logfields.append('ua=%s' % unicode2utf8(ctx.env.get('HTTP_USER_AGENT', '')))
        logfields.append('ret=%s' % (unicode2utf8(ret if isinstance(ret, basestring) else '')))
        logfields.append('ref=%s' % unicode2utf8(ctx.env.get('HTTP_REFERER', '')))

        try:
            log.note(fmt_log(' '.join(logfields)))
        except Exception, e:
            log.error('%s - %s' % (e, logfields))

    return ret


app_handler = web.application(urls, globals(), SERVER_HOT)
app_handler.add_processor(api_log)


def main():
    # print 'version:', settings.__version__
    # print 'git version:', settings.__git_version__
    # print 'release time', settings.__release_time__

    app_handler.run()


if __name__ == '__main__':
    main()

log.info(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
application = app_handler.wsgifunc()
