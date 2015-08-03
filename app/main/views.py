'''
Created on 2015年8月2日

@author: wangxun
'''
from flask import render_template, session, redirect, url_for, flash
from app.tools import ExportXmlByBeyondsoft
from app.main.forms import NameForm,XmlForm,dailyreportForm,successForm
import os
from win32api import ShellExecute
from win32con import SW_SHOWNORMAL   
from . import main    
import pymysql
from ..email import send_email
from audioop import tomono
from pip._vendor.pkg_resources import issue_warning

createtable = "create table dailyreport(\
email char (255),\
today char(255) character set gbk ,\
tomorrow char(255) character set gbk,\
issue char(255) character set gbk,\
data timestamp\
)"
createtable = "create table member(department char (255) character set gbk,\
member char(255) character set gbk \
)"

@main.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    conn = pymysql.connect(host = "69.164.202.55",user = "test",passwd = "test",db = "test",port = 3306,charset = "utf8")
    cur = conn.cursor()
    if form.validate_on_submit():
        cur.execute("select username from users1 where username = %s",form.name.data)
        username = cur.fetchone()
        if username is None:
            session['known'] = False

            send_email("troy.wang@beyondsoft.com", 'New User',
            'mail/new_user',username = form.name.data)
        else:
            session['known'] = True
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('.index'))
    return render_template('index.html',
    form = form, name = session.get('name'),
    known = session.get('known', False))
    
@main.route('/dailyreport', methods=['GET', 'POST'])
def dailyreport():
    form = dailyreportForm()
    conn = pymysql.connect(host = "69.164.202.55",user = "test",passwd = "test",db = "test",port = 3306,charset = "utf8")
    cur = conn.cursor()

    if form.validate_on_submit():
        email = str(form.email.data)
        today = str(form.today.data)
        tomorrow = str(form.tomorrow.data)
        issue = str(form.issue.data)
        cur.execute("INSERT INTO dailyreport(email, today, tomorrow, issue) VALUES ( '%s', '%s', '%s', '%s' )" % (email,today,tomorrow,issue))                                                                                       
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('.index'))
    return render_template('dailyreport.html',form = form)

@main.route('/success', methods=['GET', 'POST'])
def success():
    form = successForm()
    conn = pymysql.connect(host = "69.164.202.55",user = "test",passwd = "test",db = "test",port = 3306,charset = "utf8")
    cur = conn.cursor()

    if form.validate_on_submit():
        depart = "test"
        cur.execute("select * from member where department = '%s'" % depart)
        result = cur.fetchall()
        cur.close()
        conn.close()
        i = 0 
        while i<len(result):
            send_email(result[i][1], 'New User',
            'mail/notify',email = result[i][1],team = depart)
            i = i+1
        return redirect(url_for('.index'))
    return render_template('success.html',form = form)    
    
    
@main.route('/xml', methods=['GET', 'POST'])
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
                        ShellExecute(0,"open",xmlfile,"","",SW_SHOWNORMAL)
                        flash('成功转换成XML文件')

                    except:
                        flash('请参照用例模板设计用例')

                    
                else:
                    os.mkdir(output)
                    xmlfile = output.replace('/',"\\")+"\\"+xmlname+".xml"
                    aa =ExportXmlByBeyondsoft.changetoxml(excelname,sheetname,output,xmlname)
                    try:                      
                        aa.run()
                        ShellExecute(0,"open",xmlfile,"","",SW_SHOWNORMAL)
                        flash('成功转换成XML文件')

                    except:
                        flash('请参照用例模板设计用例')
            else:

                flash('表格名不存在')
                
        else:
            flash('用例文件不存在')
        return redirect(url_for('.success'))
    return render_template('xml.html', form=form) 