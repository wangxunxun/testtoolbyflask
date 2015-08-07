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
from ..models import db,Member,DaliyReport,Team_member
import datetime
from app.models import Team
from app.tools import CommonMethod
from app.tools import AutoSendEmail
from ..decorators import admin_required, permission_required
from ..models import Permission
from flask_login import login_user,logout_user,login_required,current_user

@main.route('/admin')
@login_required
@admin_required
def for_admins_only():
    return "For administrators!"

@main.route('/moderator')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def for_moderators_only():
    return "For comment moderators!"


@main.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():

        return redirect(url_for('.index'))
    return render_template('index.html',
    form = form)
    
@main.route('/sendenotifymail', methods=['GET', 'POST'])
@login_required
@admin_required
def sendenotifymail():
    form = sendnotifyemailForm()
    email = form.email.data
    if form.validate_on_submit():  
        member = Member.query.filter_by(email = email).first()        
        teams = Team_member.query.filter_by(memberemail = email).all()
        i = 0
        teamnames = []
        while i <len(teams):
            teamnames.append(teams[i].teamname)
            i = i+1
        if member:
            name = member.name             
            i = 0
            while i <len(teamnames):   
                token = AutoSendEmail.encrypt().generate_report_token(email, name, teamnames[i], 3600)
                send_email(email, 'Daily report','mail/Copy of notify',name = name,team = teamnames[i],token=token)
                i=i+1
            flash("发送成功")
        else:
            flash("该邮箱不存在")
        return redirect(url_for('.sendenotifymail'))
    return render_template('addteam.html',form = form)



@main.route('/editreport/<token>', methods=['GET', 'POST'])
def editreport(token):
    form = editreportForm()
    if form.validate_on_submit():
        result = AutoSendEmail.encrypt().edit_report(token)
        email = result.get('email')
        name = result.get('name')
        team = result.get('team')
        today = str(form.today.data)
        tomorrow = str(form.tomorrow.data)
        issue = str(form.issue.data)  
        report = DaliyReport(email = email,team = team,name = name,today = today,tomorrow = tomorrow,issue = issue,datetime = datetime.datetime.now())
        db.session.add(report)
        db.session.commit()
        flash("发送成功")
        return redirect(url_for('.success'))
    return render_template('dailyreport.html',form = form)

    
@main.route('/dailyreport', methods=['GET', 'POST'])
def dailyreport():
    form = dailyreportForm()
    if form.validate_on_submit():
        email = str(form.email.data)
        name = form.name.data
        team = form.team.data
        today = str(form.today.data)
        tomorrow = str(form.tomorrow.data)
        issue = str(form.issue.data)
        if Member.query.filter_by(email = email).first():    
            if Team.query.filter_by(name = team).first():    
                report = DaliyReport(email = email,name = name,team = team,today = today,tomorrow = tomorrow,issue = issue,datetime = datetime.datetime.now())
                db.session.add(report)
                db.session.commit()
                flash("发送成功")
            else:
                flash('小组不存在')
        else:
            flash("邮箱不存在")
        return redirect(url_for('.dailyreport'))
    return render_template('dailyreport.html',form = form)



@main.route('/addmember', methods=['GET', 'POST'])
@login_required
@admin_required
def addmember():
    form = AddMemberForm()
    if form.validate_on_submit():
        depart = form.depatment.data
        email = form.email.data
        name = form.name.data
        departs = depart.split("，")
        print(departs)
        result = Team.query.all()
        allteams = []   
        i = 0
        while i < len(result):
            allteams.append(result[i].name)
            i = i+1
        comresult = CommonMethod.compare(departs, allteams)
        print(comresult)
        if comresult ==True:
            if not Member.query.filter_by(email = email).first():
                member = Member(email = email,name = name)
                db.session.add(member)
                db.session.commit()                        
                i = 0
                while i <len(departs):                                       
                    member_id = Member.query.filter_by(email = email).first().id
                    team_id = Team.query.filter_by(name = departs[i]).first().id
                    teammember = Team_member(teamid = team_id,teamname = departs[i],memberid = member_id,memberemail = email)
                    db.session.add(teammember)
                    db.session.commit()                    
                    i= i+1
                flash("添加成功")
            else:
                member = Member.query.filter_by(email = email).first()
                member.name = name
                db.session.add(member)
                db.session.commit()  
                oldteams = Team_member.query.filter_by(memberemail = email).all()
                i = 0
                while i <len(oldteams):
                    db.session.delete(oldteams[i])
                    i = i+1
                
                i = 0
                while i <len(departs):                                       
                    member_id = Member.query.filter_by(email = email).first().id
                    team_id = Team.query.filter_by(name = departs[i]).first().id
                    teammember = Team_member(teamid = team_id,teamname = departs[i],memberid = member_id,memberemail = email)
                    db.session.add(teammember)                
                    i= i+1
                flash("编辑成功")
                

        else:
            flash("有些小组不存在"+str(comresult))
                
        return redirect(url_for('.addmember'))
    return render_template('addmember.html',form = form)
@main.route('/addteam', methods=['GET', 'POST'])
@login_required
@admin_required
def addteam():
    form = AddTeamForm()
    if form.validate_on_submit():      
        team = form.team.data
        result = Team.query.filter_by(name = team).first() 
        if not result:
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
        db.drop_all()
        db.create_all()       
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
                        return redirect(url_for('.success'))

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
                        return redirect(url_for('.success'))

                    except:
                        flash('请参照用例模板设计用例')
            else:

                flash('表格名不存在')
                
        else:
            flash('用例文件不存在')
        return redirect(url_for('.xml'))
    return render_template('xml.html', form=form) 


    