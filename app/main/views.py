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
from ..tools import AutoSendMail


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


    if form.validate_on_submit():  
        member = Member.query.filter_by(email = form.email.data).first()
        if member:
            email = member.email
            name = member.name
            teams = member.team_name
            newteams = teams.split("/#/")
             
            i = 0
            while i <len(newteams):   
                token = AutoSendMail.encrypt().generate_report_token(email, name, newteams[i], 3600)
                send_email(email, 'Daily report','mail/Copy of notify',name = name,team = newteams[i],token=token)
                i=i+1
        else:
            flash("该邮箱不存在")
        return redirect(url_for('.sendenotifymail'))
    return render_template('addteam.html',form = form)



@main.route('/editreport/<token>', methods=['GET', 'POST'])
def editreport(token):
    form = editreportForm()
    if form.validate_on_submit():

        result = AutoSendMail.encrypt().edit_report(token)
        print(result)
        emailresult = Member.query.all() 
        emails = SqlOperate.getAllMemberEmail(emailresult)
        email = result[0]
        name = result[1]
        team = result[2]
        today = str(form.today.data)
        tomorrow = str(form.tomorrow.data)
        issue = str(form.issue.data)
        if email in emails:        
            report = DaliyReport(email = email,team = team,name = name,today = today,tomorrow = tomorrow,issue = issue,datetime = datetime.datetime.now())
            db.session.add(report)
            db.session.commit()
            flash("发送成功")
        else:
            flash("邮箱不存在")
        return redirect(url_for('.success'))
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
                eteam = Team.query.filter_by(name = depart).first()
                oldmember = eteam.member
                if oldmember:
                    newmember = oldmember + "/#/" +email
                    eteam.member = newmember    
                    db.session.add(eteam)                   
                else:
                    eteam.member = email
                    db.session.add(eteam)
                db.session.add(member)
                db.session.commit()
                flash("添加成功")
            else:
                nm = Member.query.filter_by(email = email).first()
                oldteam = nm.team_name
                teams = oldteam.split("/#/")
                if depart not in teams:
                    newteam = oldteam + "/#/" +depart
                    nm.team_name = newteam
                    eteam = Team.query.filter_by(name = depart).first()
                    oldmember = eteam.member
                    if oldmember:
                        newmember = oldmember + "/#/" +email
                        eteam.member = newmember    
                        db.session.add(eteam)                   
    
                    else:
                        eteam.member = email
                        db.session.add(eteam)
                                                                  
                    db.session.add(nm)
                    db.session.commit()
                    flash("添加成功")
                else:
                    flash("该人员已加入该小组")
                
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
    if form.validate_on_submit():
#        db.drop_all()
#        db.create_all()       
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