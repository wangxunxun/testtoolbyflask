from flask import Flask, render_template, session, redirect, url_for, flash
from flask_script import Manager
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required
from tools import ExportXmlByBeyondsoft
from flask_wtf.file import FileField
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'

manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)


class NameForm(Form):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')

class XmlForm(Form):
    excelname = StringField('excel name', validators=[Required()])
    sheetname = StringField('sheet name', validators=[Required()])
    output = StringField('output name', validators=[Required()])
    xmlname = StringField('xmlname name', validators=[Required()])
    submit = SubmitField('Submit')
    
    
    
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            flash('Looks like you have changed your name!')
        session['name'] = form.name.data
        return redirect(url_for('index'))
    return render_template('index.html', form=form, name=session.get('name'))

@app.route('/xml', methods=['GET', 'POST'])
def xml():
    form = XmlForm()
    if form.validate_on_submit():
        excelname = form.excelname.data
        sheetname = form.sheetname.data
        output =form.output.data
        xmlname = form.xmlname.data

        flash('Looks like you have changed your name!')
        return redirect(url_for('xml'))
    return render_template('xml.html', form=form) 
    
    
        
        


if __name__ == '__main__':
    app.run()
#    manager.run()
