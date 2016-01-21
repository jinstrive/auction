# coding: utf-8
import web
import simplejson
import datetime
import logging

log = logging.getLogger()

# 2开头的错误代码第二位代表错误等级
# 0. 严重错误; 1. 普通错误; 2. 规则错误; 3. 一般信息; 4. 未知错误
class QFRET:
    OK                  = "0000"
    DBERR               = "2000"
    THIRDERR            = "2001"
    SESSIONERR          = "2002"
    DATAERR             = "2003"
    IOERR               = "2004"
    LOGINERR            = "2100"
    PARAMERR            = "2101"
    USERERR             = "2102"
    ROLEERR             = "2103"
    PWDERR              = "2104"
    REQERR              = "2200"
    IPERR               = "2201"
    MACERR              = "2202"
    NODATA              = "2300"
    DATAEXIST           = "2301"
    UNKOWNERR           = "2400"
    COUPON_OUT_RANGE    = "2500"
    COUPON_GET          = "2501"
    COUPON_CANNOT_CHANGE= "2502"
    SERVERERR           = "2600"
    ORDER_ROLE_ERROR    = "2701"
    ORDER_OVER_LIMIT_AMOUNT  = "2702"

error_map = {
    QFRET.OK                    : u"成功",
    QFRET.DBERR                 : u"数据库查询错误",
    QFRET.THIRDERR              : u"第三方系统错误",
    QFRET.SESSIONERR            : u"用户未登录",
    QFRET.DATAERR               : u"数据错误",
    QFRET.IOERR                 : u"文件读写错误",
    QFRET.LOGINERR              : u"用户登录失败",
    QFRET.PARAMERR              : u"参数错误",
    QFRET.USERERR               : u"用户不存在或未激活",
    QFRET.ROLEERR               : u"用户身份错误",
    QFRET.PWDERR                : u"密码错误",
    QFRET.REQERR                : u"非法请求或请求次数受限",
    QFRET.IPERR                 : u"IP受限",
    QFRET.MACERR                : u"MAC校验失败",
    QFRET.NODATA                : u"无数据",
    QFRET.DATAEXIST             : u"数据已存在",
    QFRET.UNKOWNERR             : u"未知错误",
    QFRET.COUPON_OUT_RANGE      : u"优惠券发放完毕",
    QFRET.COUPON_GET            : u"优惠券已领取",
    QFRET.COUPON_CANNOT_CHANGE  : u"优惠券不能修改",
    QFRET.SERVERERR             : u"内部错误",
    QFRET.ORDER_ROLE_ERROR      : u"下单用户不符合条件，有问题请咨询好近客服",
    QFRET.ORDER_OVER_LIMIT_AMOUNT  : u"购买数量已超出限制，有问题请咨询好近客服",
}

def json_default_trans(obj):
    '''json对处理不了的格式的处理方法'''
    if isinstance(obj, datetime.datetime):
        return obj.strftime('%Y-%m-%d %H:%M:%S')
    if isinstance(obj, datetime.date):
        return obj.strftime('%Y-%m-%d')
    raise TypeError('%r is not JSON serializable' % obj)

def error(errcode, resperr='', respmsg='', data=None, debug=False, escape=True, encoder=None):
    web.header('Content-Type', 'application/json; charset=UTF-8')
    global error_map
    if not resperr:
        resperr = respmsg if respmsg else error_map[errcode]
    if not respmsg:
        respmsg = resperr
    if not data:
        data = {}
    ret = {"respcd": errcode, "respmsg": respmsg, "resperr": resperr, "data": data}
    if debug:
        log.debug('error:%s', ret)
    return simplejson.dumps(ret, ensure_ascii=escape, cls=encoder, separators=(',', ':'), default = json_default_trans)

def success(data, resperr='', debug=False, escape=True, encoder=None):
    web.header('Content-Type', 'application/json; charset=UTF-8')
    ret = {"respcd": "0000", "resperr": resperr, "respmsg": "", "data": data}
    if debug:
        log.debug('success:%s', ret)
    return simplejson.dumps(ret, ensure_ascii=escape, cls=encoder, separators=(',', ':'), default = json_default_trans)


# resperr 为提示用户的错误描述
# respmsg 为错误原因提示，仅用于debug
def reterr(errcode, respmsg='', data=None):
    global error_map
    resperr = error_map[errcode]
    if not data:
        data = {}
    return {"respcd": errcode, "respmsg": respmsg, "resperr": resperr, "data": data}


def retsucc(data=None, respmsg=''):
    if not data:
        data = {}
    return {"respcd":"0000", "resperr":"", "respmsg":respmsg, "data":data}




