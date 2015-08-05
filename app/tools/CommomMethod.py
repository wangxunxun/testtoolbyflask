'''
Created on 2015年8月4日

@author: wangxun
'''
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

def generate_report_token(email,name,team,expiration=3600):
    s = Serializer('hard to guess string', expiration)
    return s.dumps({'email':email,'name':name,'team':team})


def edit_report(token):
    s = Serializer('hard to guess string')
    try:
        data = s.loads(token)
    except:
        return False
    result = []
    email = data.get('email')
    name = data.get('name')
    team = data.get('team')
    result.append(email)
    result.append(name)
    result.append(team)
    return result