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
from flask_login import UserMixin,AnonymousUserMixin
from app.exceptions import ValidationError
class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

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
    
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
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

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)
    
    def to_json(self):
        json_user = {
#            'url': url_for('api.get_post', id=self.id, _external=True),
            'id': self.id,
            'username': self.username,
            'email': self.email

        }
        return json_user
    @staticmethod
    def from_json(json_post):
        username = json_post.get('username')
        email = json_post.get('email')
        password = json_post.get('password')
        if username is None or username == '':
            raise ValidationError('post does not have a body')
        if json_post.get('id'):
            id = json_post.get('id')
            return User(id = id, username=username,email = email,password = password)
        else:
            return User(username=username,email = email,password = password)

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'],
                       expires_in=expiration)
        return s.dumps({'id': self.id}).decode('ascii')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])    
    def __repr__(self):
        return '<User %r>' % self.username

    
class DaliyReport(db.Model):
    __tablename__ = 'dailyreport'
    id = db.Column(db.Integer, primary_key=True)
    memberid = db.Column(db.Integer)
    teamid = db.Column(db.Integer)
    today = db.Column(db.String())
    tomorrow = db.Column(db.String())
    issue = db.Column(db.String())
    datetime = db.Column(db.DateTime,default = datetime.utcnow)
    def __repr__(self):
        return '<DaliyReport %r>' % self.id

class WeeklyReport(db.Model):
    __tablename__ = 'weeklyreport'
    id = db.Column(db.Integer, primary_key=True)
    memberid = db.Column(db.Integer)
    teamid = db.Column(db.Integer)
    currentweek = db.Column(db.String())
    nextweek = db.Column(db.String())
    issue = db.Column(db.String())
    datetime = db.Column(db.DateTime,default = datetime.utcnow)
    def __repr__(self):
        return '<DaliyReport %r>' % self.id
    
class Member(db.Model):
    __tablename__ = 'member'
    id = db.Column(db.Integer, primary_key=True,unique =True)
    email = db.Column(db.String(),unique =True)
    name = db.Column(db.String())
    datetime = db.Column(db.DateTime,default = datetime.utcnow)
    teams = db.relationship('Team_member', backref='member', lazy='dynamic')
    
    def __repr__(self):
        return '<Member %r>' % self.id

class Team(db.Model):
    __tablename__ = 'team'
    id = db.Column(db.Integer, primary_key=True,unique =True)
    name = db.Column(db.String(),unique =True)
    type = db.Column(db.Integer, default =1)
    datetime = db.Column(db.DateTime,default = datetime.utcnow)
    members = db.relationship('Team_member', backref='team', lazy='dynamic')

    def __repr__(self):
        return '<Team %r>' % self.id
    
class Team_member(db.Model):
    __tablename__ = 'teammember'
    id = db.Column(db.Integer, primary_key=True,unique =True)
    teamid = db.Column(db.Integer,db.ForeignKey('team.id'))
    memberid = db.Column(db.Integer,db.ForeignKey('member.id'))


    def __repr__(self):
        return '<Team_member %r>' % self.id
    
    
class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser        
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

