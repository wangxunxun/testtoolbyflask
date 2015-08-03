'''
Created on 2015年8月3日

@author: xun
'''

import pymysql
from ..email import send_email
import datetime
import time
import threading
def autosendmail():
    while True:
        if datetime.datetime.now().strftime('%H:%M:%S') == "17:26:00":
            conn = pymysql.connect(host = "69.164.202.55",user = "test",passwd = "test",db = "test",port = 3306,charset = "utf8")
            cur = conn.cursor()
            depart = "test"
            cur.execute("select * from member where department = '%s'" % depart)
            result = cur.fetchall()
            cur.close()
            conn.close()
            i = 0 
            while i<len(result):
                send_email(result[i][1], 'New User',
                'mail/notify',email = result[i][1],team = depart)
                i = i+1
            time.sleep(1)
            
