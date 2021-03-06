'''
Created on 2015年7月31日

@author: xun
'''
from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required,Email
from wtforms.fields.core import SelectField
from random import choice
from wtforms.fields.simple import TextAreaField
class NameForm(Form):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')

class XmlForm(Form):
    excelname = StringField('excel name', validators=[Required()])
    sheetname = StringField('sheet name', validators=[Required()])
    output = StringField('output name', validators=[Required()])
    xmlname = StringField('xmlname name', validators=[Required()])
    submit = SubmitField('Submit')
    
class dailyreportForm(Form):
    email = StringField('邮箱', validators=[Required(),Email()])
    name = StringField('姓名', validators=[Required()])
    team =StringField('小组', validators=[Required()])
    today = StringField('今日总结', validators=[Required()])
    tomorrow = StringField('明日计划', validators=[Required()])
    issue = StringField('遇到问题', validators=[Required()])
    submit = SubmitField('提交')
    
class editreportForm(Form):
    today = TextAreaField('今日总结', validators=[Required()])
    tomorrow = TextAreaField('明日计划', validators=[Required()])
    issue = TextAreaField('遇到问题', validators=[Required()])
    submit = SubmitField('提交')
    
class sendnotifyemailForm(Form):
    email = StringField('邮箱', validators=[Required(),Email()])
    submit = SubmitField('提交')
    
class successForm(Form):
    submit = SubmitField('提交')
    
class AddMemberForm(Form):
    depatment = StringField('小组', validators=[Required()])
    name = StringField('姓名', validators=[Required()])
    email = StringField('邮箱', validators=[Required(),Email()])
    submit = SubmitField('提交')
    
    
class AddTeamForm(Form):
    team = StringField('小组', validators=[Required()])
    teamtype = SelectField
    submit = SubmitField('提交')