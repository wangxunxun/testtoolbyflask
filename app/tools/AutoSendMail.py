'''
Created on 2015年8月3日

@author: xun
'''

import sqlite3
import os
import smtplib  
from email.mime.text import MIMEText  
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
'''
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
 '''           
class oprsql:
    def __init__(self,sql):
        self.sql = sql
        
    def getcurrentpath(self):
        homedir = os.getcwd()
        currentpath = homedir[:homedir.find("app")]
        currentpath=currentpath.replace("\\","/")
        return currentpath
    
    def getmembers(self):                
        coon = sqlite3.connect(self.getcurrentpath() +self.sql)
        cur=coon.cursor()
        cur.execute('select * from member')
        result=cur.fetchall()
        i = 0
        members = []
        while i<len(result):
            member ={}
            email = result[i][3]
            teams = result[i][1].split("/#/")
            name = result[i][2]
            member.setdefault("email",email)
            member.setdefault("teams",teams)
            member.setdefault("name",name)
            members.append(member)
            i =i +1
            
        print(members)
        return members
    
class encrypt:
    def generate_report_token(self,email,name,team,expiration=3600):
        s = Serializer('hard to guess string', expiration)
        return s.dumps({'email':email,'name':name,'team':team})
    
    def edit_report(self,token):
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
    
    
class sendmail:
    
    def __init__(self,host,user,pas,postfix):
        self.host = host
        self.user = user
        self.pas = pas
        self.postfix = postfix
        

    
    def send_mail(self,to_list,sub,content):
        me="beyondsoft.ams"+" <"+self.user+">"   #这里的hello可以任意设置，收到信后，将按照设置显示
        msg = MIMEText(content,_subtype='html',_charset='gb2312')    #创建一个实例，这里设置为html格式邮件
        msg['Subject'] = sub    #设置主题
        msg['From'] = me  
        msg['To'] = ";".join(to_list)  
        try:  
            s = smtplib.SMTP()  
            s.connect(mail_host)  #连接smtp服务器
            s.login(mail_user,mail_pass)  #登陆服务器
            s.sendmail(me, to_list, msg.as_string())  #发送邮件
            s.close()  
            return True  
        except Exception as e:
            print(e)
            return False  
        
    def autosend(self):
        members = oprsql("data.sqlite")
        members = members.getmembers()
        i = 0
        while i<len(members):
            email = members[i].get('email')
            teams = members[i].get('teams')
            name = members[i].get('name')
            j=0
            while j <len(teams):
                token = encrypt.generate_report_token(email, name, teams[j], 3600)
                token = str(token)
                token = token[2:len(token)-1]
    
                url ="http://127.0.0.1:5000/editreport/"+token
            
        
                content = "<h5>Hello "+name+",</h5>\
            <p>您今天的日报链接已经创建，请于今天18:30 前填写提交.</p>\
            <p>本日报隶属于<strong>"+teams[j]+"</strong>小组</p>\
            <p>链接地址: <a href="+url+">click here</a></p>\
            谢谢"
            
                mailto_list=[email] 

                if self.send_mail(mailto_list,"QA Team小组-日报创建提醒 ",content):  
                    print("发送成功")  
                else:  
                    print("发送失败")  
                j = j+1
                
            i =i+1        
        
        
        
        


if __name__ == '__main__':  
    
    
    mail_host="smtp.163.com"  #设置服务器
    mail_user="beyondsoftbugzilla@163.com"    #用户名
    mail_pass="wangxun2"   #口令 
    mail_postfix="163.com"  #发件箱的后缀
    a = sendmail(mail_host,mail_user,mail_pass,mail_postfix)
    a.autosend()
    
    
    

