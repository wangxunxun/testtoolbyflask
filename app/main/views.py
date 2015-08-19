'''
Created on 2015年8月2日

@author: wangxun
'''
from flask import render_template, session, redirect, url_for, flash,request
from app.tools import ExportXmlByBeyondsoft
from app.main.forms import NameForm,XmlForm,dailyreportForm,successForm,AddMemberForm,AddTeamForm,editreportForm,sendnotifyemailForm
import os
from win32api import ShellExecute
from win32con import SW_SHOWNORMAL   
from . import main    
import pymysql
from ..email import send_email
from ..models import db,Member,DaliyReport,Team_member,Team,Permission
import datetime
from app.tools import CommonMethod
from app.tools import AutoSendEmail
from ..decorators import admin_required, permission_required
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
def addmember():
    teams = Team.query.all()
    if request.method == 'POST':
        email = request.form['email']
        name = request.form['name']
        chooseteams = request.form.getlist('teams')

        if chooseteams:
            if not Member.query.filter_by(email = email).all():
                member = Member(email = email,name = name)
                db.session.add(member)
                db.session.commit()
                q_member = Member.query.filter_by(email = email).first()          
                memberid = q_member.id
                for teamname in chooseteams:
                    q_team = Team.query.filter_by(name = teamname).first()
                    teamid = q_team.id
                    team = Team_member(teamid = teamid,memberid = memberid)
                    db.session.add(team)
                db.session.commit()
                return redirect(url_for('.membermanage'))
            else:
                flash('该邮箱已注册，不能重复注册')
        else:
            flash('请选择小组')
    return render_template('addmember.html',teams = teams)


@main.route('/addteam', methods=['GET', 'POST'])
@login_required
def addteam():
    if request.method =='POST':
        teamname = request.form['teamname']
        teamtype = request.form['teamtype']
        if not Team.query.filter_by(name = teamname):
            team = Team(name = teamname,type = teamtype)
            db.session.add(team)
            db.session.commit()
            return redirect(url_for('.teammanage'))
        else:
            flash('该小组已存在，不能重复添加')
    return render_template('addteam.html')

@main.route('/deleteteam/<int:id>', methods=['GET', 'POST'])
@login_required
def deleteteam(id):
    q_team = Team.query.filter_by(id = id).first()

    q_teammembers = Team_member.query.filter_by(teamid = id).all()
    print(q_teammembers)
    for teammember in q_teammembers:
        db.session.delete(teammember)
    db.session.delete(q_team)
    db.session.commit()
    return redirect(url_for('.teammanage'))


@main.route('/deletemember/<int:id>', methods=['GET', 'POST'])
@login_required
def deletemember(id):
    q_member = Member.query.filter_by(id = id).first()

    q_teammembers = Team_member.query.filter_by(memberid = id).all()
    print(q_teammembers)
    for teammember in q_teammembers:
        db.session.delete(teammember)
    db.session.delete(q_member)
    db.session.commit()
    return redirect(url_for('.membermanage'))
@main.route('/teammanage', methods=['GET', 'POST'])
@login_required
def teammanage():
    teams = Team.query.all()
    teamdata = []
    for team in teams:
        teaminfo = {}
        teaminfo.setdefault('id',team.id)
        teaminfo.setdefault('name',team.name)
        teaminfo.setdefault('type',team.type)
        teammembers = []
        for member in team.members:
            meminfo = {}
            mem = Member.query.filter_by(id =member.memberid).first()

            meminfo.setdefault('id',mem.id)
            meminfo.setdefault('email',mem.email)
            meminfo.setdefault('name',mem.name)                
            teammembers.append(meminfo)
        teaminfo.setdefault('members',teammembers)
        teamdata.append(teaminfo)
                                  
    return render_template('teammanage.html',teams = teamdata)

@main.route('/membermanage', methods=['GET', 'POST'])
@login_required
def membermanage():
    members = Member.query.all()
    membersdata = []        
    for member in members:
        memberinfo = {}
        memberinfo.setdefault('id',member.id)
        memberinfo.setdefault('email',member.email)
        memberinfo.setdefault('name',member.name)
        teams = []
        for team in member.teams:
            data = Team.query.filter_by(id = team.teamid).first()
            teaminfo = {}
            teaminfo.setdefault('id',data.id)
            teaminfo.setdefault('type',data.type)
            teaminfo.setdefault('name',data.name)
            teams.append(teaminfo)
        memberinfo.setdefault('teams',teams)
        membersdata.append(memberinfo) 
    print(membersdata)     
    return render_template('membermanage.html',members = membersdata)


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
    print(request.method)
    
    if request.method =='POST':
        print(request.method)
        print(request.form['excel'])
        flash('3433')

        return render_template('xml.html') 
    return render_template('xml.html') 
    
    
    
'''    
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
'''

    