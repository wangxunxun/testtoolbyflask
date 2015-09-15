# -*- coding: utf-8 -*-
import json
import uuid
import time
import sys

sessionDB = {
    "763c962e3f3011e588bdb8975a9c70dc":{
        "create_time":1440050411,
        "update_time":1440050411,
        "user_id":1
    }
}

order_status_info = {
    1:"待付款（订单创建成功）",
    2:"已取消（未成功付款，取消的订单）",
    3:"已结束（订单消费结束的状态）",
    4:"已付定金（包车订单首付款）",
    5:"已锁定（包车订单订金支付后取消订单，该订单未支付成功，不走申请退款流程）",
    6:"支付确认中（付款等待回调）",
    7:"已支付（支付回调完成）",
    8:"退款处理中（订单退订申请受理）",
    9:"已退款（订单金额已经退完）",
    10:"估价中(包车下订单未确认时状态)"
}

code_message = {
    0:'',
    1:'Session过期',
    2:"参数错误",
    3:"权限不够",
    4:"您的请求被拒绝,请先登录",
    5:"登录失败,用户名或者密码错误",
    6:"电话号码已经注册",
    7:"此号码未注册，请先注册",
    8:"密码错误",
    9:"验证码错误或超时",
    10:"您的版本已经过时，请尽快更新",

    21:"您购买的路线不存在或者已变更，请重新查询购买",
    22:"您购买的路线余票不足",

    30:"您的用户名已经被占用，请重新设置",
    31:"您的邮箱已经注册，请重新设置",
    32:"您请求的订单不存在",
    33: "您的订单状态不能退款， 订单状态为：",
    34:'您的订单支付申请失败，价格与订单实际价格不符',

    100:"您的订单不是未付款状态，不能直接取消订单"
}

def getUserID(sessionID):
    return sessionDB[sessionID]["user_id"];

def newSession(user_id):
    sessionID = uuid.uuid1().hex
    sessionDB[sessionID] = {
        "create_time":time.time(),
        "update_time":time.time(),
        "user_id":user_id
    }
    return sessionID


def destorySession(session):
    sessionDB.pop(session)


def destorySessionPostAboutMe(sessionID, memberID):
    for session in sessionDB.keys():
        if session != sessionID:
            if sessionDB[session]["user_id"] == memberID:
                sessionDB.pop(session)


def destorySessionAll(memberID):
    for session in sessionDB.keys():
        if sessionDB[session]["user_id"] == memberID:
            sessionDB.pop(session)


def parent_reload(url="/Server/Administrator/Role"):
    return '''<script>var index = parent.layer.getFrameIndex(window.iframe);
    window.parent.location.href="'''+ url + '''";</script>'''

successStr = '''{"response":{"code":0,"message":""}}'''


def errorStr(code, obj=None, string=""):
    if obj is None:
        return '''{"response":{"code":''' + str(code) + ''',"message":"''' + code_message[code] + string + '''"}}'''
    else:
        so = {
            'response':{
                'code':code,
                'message':code_message[code]
            }
        }

        for o in obj:
            so[o] = obj[o]
        
        return json.dumps(so, separators=(',', ':'))


def successDataStr(obj):
    so = {
        'response':{
            'code':0,
            'message':''
        }
    }

    for o in obj:
        so[o] = obj[o]

    print(so)
    return json.dumps(so, separators=(',',':'))
