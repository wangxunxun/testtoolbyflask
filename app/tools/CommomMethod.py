'''
Created on 2015年8月4日

@author: wangxun
'''
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

def generate_report_token(email,name,expiration=3600):
    s = Serializer('hard to guess string', expiration)
    return s.dumps({'email':email,'name':name})


def edit_report(token):
    s = Serializer('hard to guess string')
    try:
        data = s.loads(token)
    except:
        return False
    result = []
    email = data.get('email')
    name = data.get('name')
    result.append(email)
    result.append(name)
    return result