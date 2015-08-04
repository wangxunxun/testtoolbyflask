'''
Created on 2015年8月4日

@author: xun
'''
from datetime import datetime
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request
from . import db
from . import login_manager
from flask_login import UserMixin



class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin,db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True
    
    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})


    def __repr__(self):
        return '<User %r>' % self.username
    
    
class DaliyReport(db.Model):
    __tablename__ = 'dailyreport'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255))
    name = db.Column(db.String(255))
    today = db.Column(db.String(255))
    tomorrow = db.Column(db.String(255))
    issue = db.Column(db.String(255))
    datetime = db.Column(db.DateTime)
    def __repr__(self):
        return '<DaliyReport %r>' % self.email
    
class Member(db.Model):
    __tablename__ = 'member'
    id = db.Column(db.Integer, primary_key=True)
    team_name = db.Column(db.String(255),db.ForeignKey('team.name'))
    name = db.Column(db.String(255))
    email = db.Column(db.String(255),unique =True)
    def __repr__(self):
        return '<Member %r>' % self.name

class Team(db.Model):
    __tablename__ = 'team'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255),unique =True)
    member = db.relationship('Member', backref='team', lazy='dynamic')

    def __repr__(self):
        return '<Team %r>' % self.name
    
    
    
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))