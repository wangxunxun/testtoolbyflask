'''
Created on 2015年7月31日

@author: xun
'''
import os
from app import create_app,db

from flask_script import Manager,Shell
from app.models import User,Role
from flask_migrate import MigrateCommand,Migrate
from config import Config
from queue import Queue
from app.tools.AutoSendEmail import Consumer,Producer
from ctypes.test.test_errno import threading
from app.tools.AutoSendEmail import sendmail

host = Config.host
port = Config.port

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

manager = Manager(app)
migrate = Migrate(app, db)
def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


    

    
if __name__ == '__main__':
    mail_host="smtp.163.com"  #设置服务器
    mail_user="beyondsoftbugzilla@163.com"    #用户名
    mail_pass="wangxun2"   #口令 
    sql = 'C:/Users/xun/workspace/testtoolbyflask/data.sqlite'
    a = sendmail(mail_host,mail_user,mail_pass,sql)
#    t =threading.Thread(target=a.dingshi)
#    t.start()
    app.run()
#    manager.run()



    
