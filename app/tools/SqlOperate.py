'''
Created on 2015年8月4日

@author: xun
'''



def getAllTeamName(result):
    teams = []   
    i = 0
    while i < len(result):
        teams.append(result[i].name)
        i = i+1
    return teams

def getAllMemberEmail(result):
    emails = []
    i = 0
    while i < len(result):
        emails.append(result[i].email)
        i = i+1  
    return emails