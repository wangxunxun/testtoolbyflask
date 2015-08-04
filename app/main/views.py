'''
Created on 2015年8月2日

@author: wangxun
'''
from flask import render_template, session, redirect, url_for, flash
from app.tools import ExportXmlByBeyondsoft
from app.main.forms import NameForm,XmlForm,dailyreportForm,successForm,AddMemberForm,AddTeamForm,editreportForm,sendnotifyemailForm
import os
from win32api import ShellExecute
from win32con import SW_SHOWNORMAL   
from . import main    
import pymysql
from ..email import send_email
from ..models import db,Member,DaliyReport
import datetime
from app.models import Team
from ..tools import SqlOperate
from ..tools import CommomMethod


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
    if form.validate_on_submit():

        return redirect(url_for('.index'))
    return render_template('index.html',
    form = form)
    
@main.route('/sendenotifymail', methods=['GET', 'POST'])
def sendenotifymail():
    form = sendnotifyemailForm()
    token = CommomMethod.generate_report_token("59853844@qq.com", "wangxun", 3600)
    if form.validate_on_submit():      
        send_email(form.email.data, 'New User','mail/Copy of notify',name = "test",team = "ceshi",token=token)
        return redirect(url_for('.sendenotifymail'))
    return render_template('addteam.html',form = form)



@main.route('/editreport/<token>', methods=['GET', 'POST'])
def editreport(token):
    form = editreportForm()
    if form.validate_on_submit():
        result = CommomMethod.edit_report(token)
        emailresult = Member.query.all() 
        emails = SqlOperate.getAllMemberEmail(emailresult)
        email = result[0]
        name = result[1]
        print(email)
        print(name)
        today = str(form.today.data)
        tomorrow = str(form.tomorrow.data)
        issue = str(form.issue.data)
        if email in emails:        
            report = DaliyReport(email = email,name = name,today = today,tomorrow = tomorrow,issue = issue,datetime = datetime.datetime.now())
            db.session.add(report)
            db.session.commit()
            flash("发送成功")
        else:
            flash("邮箱不存在")
        return redirect(url_for('.dailyreport'))
    return render_template('dailyreport.html',form = form)

    
@main.route('/dailyreport', methods=['GET', 'POST'])
def dailyreport():
    form = dailyreportForm()

    


    if form.validate_on_submit():
        emailresult = Member.query.all() 
        emails = SqlOperate.getAllMemberEmail(emailresult)
        email = str(form.email.data)
        name = form.name.data
        today = str(form.today.data)
        tomorrow = str(form.tomorrow.data)
        issue = str(form.issue.data)
        if email in emails:
        
            report = DaliyReport(email = email,name = name,today = today,tomorrow = tomorrow,issue = issue,datetime = datetime.datetime.now())
            db.session.add(report)
            db.session.commit()
            flash("发送成功")
        else:
            flash("邮箱不存在")
        return redirect(url_for('.dailyreport'))
    return render_template('dailyreport.html',form = form)

@main.route('/addmember', methods=['GET', 'POST'])
def addmember():
    form = AddMemberForm()
    result = Team.query.all() 
    teams =SqlOperate.getAllTeamName(result)
    emailresult = Member.query.all() 
    emails = SqlOperate.getAllMemberEmail(emailresult)   
    if form.validate_on_submit():
        depart = form.depatment.data
        email = form.email.data
        name = form.name.data
        if depart in teams:
            if email not in emails:
                
                member = Member(team_name = depart,email = email,name = name)
                db.session.add(member)
                db.session.commit()
                flash("添加成功")
            else:
                flash("邮箱已注册")
        else:
            flash("小组不存在")
        return redirect(url_for('.addmember'))
    return render_template('addmember.html',form = form)
@main.route('/addteam', methods=['GET', 'POST'])
def addteam():
    form = AddTeamForm()
    if form.validate_on_submit():      
        team = form.team.data
        result = Team.query.all() 
        teams = SqlOperate.getAllTeamName(result)
        if team not in teams:
            team_db = Team(name = team)
            db.session.add(team_db)
            db.session.commit()
            flash("添加成功")
        else:
            flash("这个小组已经存在")
        return redirect(url_for('.addteam'))
    return render_template('addteam.html',form = form)


@main.route('/success', methods=['GET', 'POST'])
def success():
    form = successForm()
    db.drop_all()
    db.create_all()

    if form.validate_on_submit():


        result = Member.query.all()
        print(result)
        i = 0 
        while i<len(result):
#            send_email(result[i].email, 'New User','mail/notify',name = result[i].name,team = result[i].team_name)
            i = i+1
         
        return redirect(url_for('.success'))
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