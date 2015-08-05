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

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True    
    
    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        return True


    def __repr__(self):
        return '<User %r>' % self.username
    
    
class DaliyReport(db.Model):
    __tablename__ = 'dailyreport'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255))
    team = db.Column(db.String(255))
    name = db.Column(db.String(255))
    today = db.Column(db.String(255))
    tomorrow = db.Column(db.String(255))
    issue = db.Column(db.String(255))
    datetime = db.Column(db.DateTime)
    def __repr__(self):
        return '<DaliyReport %r>' % self.email
    
class Member(db.Model):
    __tablename__ = 'member'
    id = db.Column(db.Integer, primary_key=True,unique =True)
    email = db.Column(db.String(255),unique =True)
    name = db.Column(db.String(255))
    
    def __repr__(self):
        return '<Member %r>' % self.name

class Team(db.Model):
    __tablename__ = 'team'
    id = db.Column(db.Integer, primary_key=True,unique =True)
    name = db.Column(db.String(255),unique =True)

    def __repr__(self):
        return '<Team %r>' % self.name
    
class Team_member(db.Model):
    __tablename__ = 'teammember'
    id = db.Column(db.Integer, primary_key=True,unique =True)
    teamid = db.Column(db.Integer)
    teamname = db.Column(db.String(255))
    memberid = db.Column(db.Integer)
    memberemail = db.Column(db.String(255))

    def __repr__(self):
        return '<Team_member %r>' % self.teamid
    
    
    
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))