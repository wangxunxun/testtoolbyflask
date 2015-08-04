'''
Created on 2015年8月3日

@author: xun
'''


from flask import Blueprint
auth = Blueprint('auth', __name__)
from . import views