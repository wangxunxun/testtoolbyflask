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


    app.run(host=host,port=port)
#    manager.run()



    
