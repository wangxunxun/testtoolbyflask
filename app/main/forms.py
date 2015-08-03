'''
Created on 2015年7月31日

@author: xun
'''
from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required
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
    email = StringField('邮箱', validators=[Required()])
    today = StringField('今日总结', validators=[Required()])
    tomorrow = StringField('明日计划', validators=[Required()])
    issue = StringField('遇到问题', validators=[Required()])
    submit = SubmitField('提交')
    
class successForm(Form):
    submit = SubmitField('提交')