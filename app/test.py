from flask import Flask, render_template, session, redirect, url_for, flash
from flask_script import Manager
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required
from tools import ExportXmlByBeyondsoft
from flask_wtf.file import FileField
from forms import NameForm,XmlForm
import os
from win32api import ShellExecute
from win32con import SW_SHOW, SW_SHOWNOACTIVATE, SW_SHOWNORMAL
app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'

manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)



    
    
    
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
        if os.path.exists(excelname):
            try:     
                sheets = ExportXmlByBeyondsoft.exceloperate(excelname).getSheetNames()   
            except:
                flash('该用例文件没有表格')

            
            if sheetname in sheets:
                if os.path.exists(output):
                    
                    xmlfile = output.replace('/',"\\")+"\\"+xmlname+".xml"
                    aa =ExportXmlByBeyondsoft.changetoxml(excelname,sheetname,output,xmlname)  
                    try:                      
                        aa.run()
                        ShellExecute(0,"open",xmlfile,"","",SW_SHOWNOACTIVATE)
                        flash('成功转换成XML文件')

                    except:
                        flash('请参照用例模板设计用例')

                    
                else:
                    os.mkdir(output)
                    xmlfile = output.replace('/',"\\")+"\\"+xmlname+".xml"
                    aa =ExportXmlByBeyondsoft.changetoxml(excelname,sheetname,output,xmlname)
                    try:                      
                        aa.run()
                        ShellExecute(0,"open",xmlfile,"","",SW_SHOWNOACTIVATE)
                        flash('成功转换成XML文件')

                    except:
                        flash('请参照用例模板设计用例')
            else:

                flash('表格名不存在')
                
        else:
            flash('用例文件不存在')
        return redirect(url_for('xml'))
    return render_template('xml.html', form=form) 
    
    
        
        


if __name__ == '__main__':
    app.run()
#    manager.run()