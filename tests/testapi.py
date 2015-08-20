'''
Created on 2015年8月19日

@author: xun
'''
import httplib2  
from urllib.parse import urlencode
import json
import xlwt
import sqlite3
import xlrd
from dominate.tags import table
import datetime


class oprsql:
    def __init__(self,sqlpath):
        self.sqlpath = sqlpath
        self.cx = sqlite3.connect(sqlpath)
        self.cu = self.cx.cursor()

    def getTablesName(self):
        self.cu.execute('select name from sqlite_master where type = "table" order by name')        
        tables = self.cu.fetchall()
        tablesname = []
        i = 0
        while i <len(tables):
            tablesname.append(tables[i][0])
            i = i+1
        return tablesname
    
    def getTableHeader(self,tablename):
        self.cu.execute('PRAGMA table_info(%s)'%tablename)
        tables = self.cu.fetchall()
        header = []
        for i in tables:
            header.append(i[1])          
        return header
    
    def getTableData(self,tablename):
        self.cu.execute('select * from %s'%tablename)
        data = self.cu.fetchall()
        return data
    
    def getTablesHeader(self,tablesname):
        data = {}
        for tablename in tablesname:
            self.cu.execute('PRAGMA table_info(%s)'%tablename)
            tables = self.cu.fetchall()
            header = []
            for i in tables:
                header.append(i[1])   
            data.setdefault(tablename,header)                                   
        return data
    
    def getTablesData(self,tablesname):
        data = {}
        for tablename in tablesname:
            self.cu.execute('select * from %s'%tablename)
            tabledata = self.cu.fetchall()
            data.setdefault(tablename,tabledata)
        return data
    
    def closeSQLConnect(self):
        self.cx.close()
                
class oprexcel:
    def __init__(self,excelpath):
        self.excelpath = excelpath
    
    def saveTable(self,tablename,tableheader,tabledata):
        f = xlwt.Workbook()
        sheet1 = f.add_sheet(tablename,cell_overwrite_ok=True) 
        for i in range(0,len(tableheader)):
            sheet1.write(0,i,tableheader[i])
        i = 0
        while i < len(tabledata):
            for j in range(0,len(tabledata[i])):
                sheet1.write(i+1,j,tabledata[i][j])
            i = i+1
        f.save(self.excelpath)
        
    def saveTables(self,tablesname,tablesheader,tablesdata):
        f = xlwt.Workbook()
        for tablename in tablesname:
            sheet1 = f.add_sheet(tablename,cell_overwrite_ok=True) 
            for i in range(0,len(tablesheader.get(tablename))):
                sheet1.write(0,i,tablesheader.get(tablename)[i])
            i = 0
            while i < len(tablesdata.get(tablename)):
                for j in range(0,len(tablesdata.get(tablename)[i])):
                    sheet1.write(i+1,j,tablesdata.get(tablename)[i][j])
                i = i+1            
        f.save(self.excelpath)
        
class sqltoExcel():
    def __init__(self,sqlpath,excelpath):
        self.sqlpath = sqlpath
        self.excelpath = excelpath
        
    def run(self):
        sql = oprsql(self.sqlpath)       
        tablesname = sql.getTablesName()
        tablesheader = sql.getTablesHeader(tablesname)
        tablesdata = sql.getTablesData(tablesname)
        sql.closeSQLConnect()
        excel = oprexcel(self.excelpath)
        excel.saveTables(tablesname, tablesheader, tablesdata)
        
class readExcel():
    def __init__(self,excelpath):
        self.excelpath = excelpath
        
    def readTable(self,tablename):
        data = xlrd.open_workbook(self.excelpath)
        table = data.sheet_by_name(tablename)
        nrows = table.nrows
        ncols = table.ncols
        header = table.row_values(0)
        tabledata = []
        i = 1
        while i < nrows:
            rdata = table.row_values(i)
            j = 0
            row = {}
            while j <len(header):                
                row.setdefault(header[j],rdata[j])
                j = j+1           
            tabledata.append(row)
            i=i+1
        print(tabledata)
        return tabledata
    
    def readTables(self,tablesname):
        data = xlrd.open_workbook(self.excelpath)
        tablesdata = {}
        for tablename in tablesname:
            table = data.sheet_by_name(tablename)
            nrows = table.nrows
            ncols = table.ncols
            header = table.row_values(0)
            tabledata = []
            i = 1
            while i < nrows:
                rdata = table.row_values(i)
                if isinstance(rdata[0],float):
                    rdata[0] = int(rdata[0])
                j = 0
                row = {}
                while j <len(header):                
                    row.setdefault(header[j],rdata[j])
                    j = j+1           
                tabledata.append(row)
                i=i+1
            tablesdata.setdefault(tablename,tabledata)
        print(tablesdata)
        return tablesdata

class sendAPI:
    def __init__(self,url,data,method='POST',contentType = 'json'):
        self.url =url
        self.data = data
        self.method = method
        self.contentType = contentType
        
    def run(self):
        if self.method == 'POST' and self.contentType == 'json':
            successCount = 0
            failCount =0
            h = httplib2.Http(".cache")  
            result = {}
            start = datetime.datetime.now()
            for i in self.data:
                encodedjson = json.dumps(i)   
                resp, content = h.request(self.url, self.method,encodedjson, headers={"Content-Type": "application/%s"%self.contentType} )  
                if resp.get('status')=='200':
                    successCount = successCount +1
                else:
                    failCount = failCount +1
                
            end = datetime.datetime.now()

            duration = end - start
            duration =  duration.seconds +duration.microseconds/1000000
            result.setdefault('duration',duration)
            result.setdefault('successCount',successCount)
            result.setdefault('failCount',failCount)
            print(result)
            return result
        else:
            print('no support')
 
                    
        


if __name__ == '__main__':
    to = sqltoExcel("C:/users/xun/workspace/testtoolbyflask/data.sqlite",'D:/demo.xls')
#    to.run()
    rexcel = readExcel('D:/demo.xls')
    rexcel.readTables(['users'])
    h = httplib2.Http(".cache")  
    data = dict(email = 24443, username="Atesco4433353mmen33t",password = '12343')
    encodedjson = json.dumps(data)    
    userdata = rexcel.readTable('users')
    print(userdata)    
    cc = sendAPI("http://127.0.0.1:5000/api/v1.0/users/",userdata)
    cc.run()
