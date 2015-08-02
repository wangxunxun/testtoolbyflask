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