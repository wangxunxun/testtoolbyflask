'''
Created on 2015年8月3日

@author: xun
'''
from flask import Blueprint
main = Blueprint('main', __name__)
from . import views,errors