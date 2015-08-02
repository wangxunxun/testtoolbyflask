#coding=utf-8
'''
Created on 2015年7月28日

@author: xun
'''
from xml.dom import minidom
import xlrd
import os
from idlelib.IOBinding import encoding



class exportxml:
    def __init__(self,sheetname,testdata,outputfolder,filename):
        self.testdata = testdata
        self.output = outputfolder
        self.filename = filename
        self.sheetname = sheetname
        
    def export(self):

        impl = minidom.getDOMImplementation()
        dom = impl.createDocument(None, None, None)
        inittestsuite = dom.createElement("testsuite")
        inittestsuite.setAttribute("name", "")   
        sheetsuite = dom.createElement("testsuite")
        sheetsuite.setAttribute("name", self.sheetname)
        inittestsuite.appendChild(sheetsuite)
        i=0
        bigsuite_s =[]
        while i<len(self.testdata):                        
            bigsuite =  dom.createElement("testsuite")                    
            bigsuite_s.append(bigsuite)    
            bigsuite_s[i].setAttribute("name", str(self.testdata[i].get("bigsuite")))     
            suite_s = []             
            j=0
            while j<len(self.testdata[i].get("suite")):        
                suite = dom.createElement("testsuite")
                suite_s.append(suite)
                suite_s[j].setAttribute("name", str(self.testdata[i].get("suite")[j]))                                                 
                testcase_s=[]
                summary_s =[]
                preconditions_s =[]
                importance_s =[]

                k = 0
                while k < len(self.testdata[i].get("cases")[j]):


                    testcase = dom.createElement("testcase")
                    testcase_s.append(testcase)
                    
                    summary = dom.createElement("summary")
                    summary_s.append(summary)
                    preconditions = dom.createElement("preconditions")
                    preconditions_s.append(preconditions)
                    importance = dom.createElement("importance")
                    importance_s.append(importance)
                                      
                    summary_text = dom.createTextNode(str(self.testdata[i].get("cases")[j][k].get("summary")))               
                    preconditions_text = dom.createTextNode(str(self.testdata[i].get("cases")[j][k].get("preconditions")))
                    importance_text = dom.createTextNode(str(self.testdata[i].get("cases")[j][k].get("importance")))            
                    
                    testcase_s[k].setAttribute("name", str(self.testdata[i].get("cases")[j][k].get("name")))                                                         
                    summary_s[k].appendChild(summary_text)                
                    preconditions_s[k].appendChild(preconditions_text)                
                    importance_s[k].appendChild(importance_text)
                    
                    
                    testcase_s[k].appendChild(summary_s[k])
                    testcase_s[k].appendChild(preconditions_s[k])
                    testcase_s[k].appendChild(importance_s[k])

                    
                    suite_s[j].appendChild(testcase_s[k])
                    
                    
                    k = k+1
                bigsuite_s[i].appendChild(suite_s[j])
                j = j+1 
            sheetsuite.appendChild(bigsuite_s[i])
            i=i+1    
        dom.appendChild(inittestsuite)
        f=open(self.output+"/"+self.filename+".xml",'w',encoding = "utf-8")
        dom.writexml(f,'',' ','\n','utf-8')
        f.close()
 
 
class readexcel:
    def __init__(self,testexcel,sheetname):
        self.testexcel = testexcel
        self.sheetname = sheetname
        self.data = xlrd.open_workbook(self.testexcel)
        self.table = self.data.sheet_by_name(self.sheetname)    
        
    def getsheetname(self):
        return self.sheetname
    
    def read(self):
        self.testdata = []
        self.bigsuites = []
        self.suites =[]
        self.name = []
        self.preconditions = []
        self.steps =[]
        self.output = []
        self.importance = []


        i =1
        j =self.table.nrows
        while i<j:
            if self.table.cell(i,0).value and self.table.cell(i,1).value and self.table.cell(i,3).value:

                self.bigsuites.append(self.table.cell(i,0).value)
                self.suites.append(self.table.cell(i,1).value)
                self.name.append(self.table.cell(i,3).value)
                self.preconditions.append(self.table.cell(i,5).value)
                self.steps.append(self.table.cell(i,6).value)
                self.output.append(self.table.cell(i,7).value) 
                self.importance.append(self.table.cell(i,8).value)               
                

                                
            elif not self.table.cell(i,0).value and not self.table.cell(i,1).value and self.table.cell(i,3).value:

                self.name.append(self.table.cell(i,3).value)
                self.preconditions.append(self.table.cell(i,5).value)
                self.steps.append(self.table.cell(i,6).value)
                self.output.append(self.table.cell(i,7).value) 
                self.importance.append(self.table.cell(i,8).value)   
                
            elif not self.table.cell(i,0).value and self.table.cell(i,1).value and self.table.cell(i,3).value:

                
                self.suites.append(self.table.cell(i,1).value)
                self.name.append(self.table.cell(i,3).value)
                self.preconditions.append(self.table.cell(i,5).value)
                self.steps.append(self.table.cell(i,6).value)
                self.output.append(self.table.cell(i,7).value)
                self.importance.append(self.table.cell(i,8).value)  
            i=i+1
        self.steps = self.newline(self.steps)
        self.output = self.newline(self.output)
        self.summary = self.getSummary(self.steps, self.output)

        self.cases = self.getdiccase(self.name, self.summary, self.preconditions, self.importance)
        self.testdata.append(self.bigsuites)
        self.testdata.append(self.suites)
        self.testdata.append(self.cases)


        return self.testdata 
    
    
    def newline(self,data):
        i = 0
        newdata = []
        while i<len(data):
            c = data[i].replace("\n","<br>")
            newdata.append(c)
            i = i+1
        return newdata
    
    def getSummary(self,steps,output):
        i = 0
        summary = []
        while i <len(self.steps):
            t = steps[i]
            r = output[i]
            site = "<span style='font-weight:bold;font-size:18px;color:#ee82ee;'>"+"Steps (Input)"+"</span>"+"<br>"
            re = "<span style='font-weight:bold;font-size:18px;color:#ee82ee;'>"+"Expected Output:"+"</span>"+"<br>"
            summary.append(site+t +"<br>"*3+ re +r)
            i=  i+1
        return summary
    
    def bigsuitedis(self):        
        j=1
        dis =[]        
        while j<self.table.nrows:
            if self.table.cell(j,0).value:
                dis.append(j)
            j=j+1
        dis.append(self.table.nrows)
        return dis
    
    def suitedis(self):
        j=1
        dis =[]
        while j<self.table.nrows:
            if self.table.cell(j,1).value:
                dis.append(j)
            j=j+1
        dis.append(self.table.nrows)
        return dis
    
    def nocaserow(self):
        a = self.suitedis()
        i= 0
        count = []
        while i<len(a):
            j = 0
            k =0
            while j<a[i]:
                if self.table.cell(j,3).value =="":
                    k=k+1                    
                j=j+1
            count.append(k)
            i=i+1
        return count
    
    def realsuitedis(self):
        suitedis = self.suitedis()
        nocaserow = self.nocaserow()
        realcasedis = []
        i = 0
        while i<len(suitedis):
            realrow = suitedis[i]-nocaserow[i]
            realcasedis.append(realrow)
            i=i+1
        return realcasedis
    
    def getdiccase(self,name,summary,preconditions,importance):
        data = []
        i = 0
        while i<len(name):
            case = {}
            case.setdefault("name",name[i])
            case.setdefault("summary",summary[i])
            case.setdefault("preconditions",preconditions[i])
            case.setdefault("importance",importance[i])
            data.append(case)
            i=i+1
        return data
    
    
    
    def data_case(self):
        data = self.read()
        a = self.realsuitedis()

        test =[]
        i =0
        while i<len(a)-1:
            test.append(data[2][a[i]-1:a[i+1]-1])
            i=i+1

        return test
    
    def suitecount(self,i,j):
        k=1
        start =0
        end =0
        while k<i:
            if self.table.cell(k,1).value:
                start = start +1
            k=k+1
        l=1
        while l<j:
            if self.table.cell(l,1).value:
                end = end +1
            l=l+1
        return end - start
    
    def count_suite(self):
        test =[]
        a = self.bigsuitedis()
        i =0
        while i<len(a)-1:
            bb=self.suitecount(a[i], a[i+1])
            test.append(bb)                        
            i=i+1
        return test
    
    def realCountSuite(self,data):
        i =0
        new =[0]
        while i<len(data):
            j =0 
            c = 0
            while j<=i:
                c = c+data[j]            
                j=j+1
            new.append(c)
            i = i+1
        return new
    
    def data_suite(self):
        data = self.read()
        a = self.realCountSuite(self.count_suite())

        i=1
        allsuite=[]        
        while i<len(a):

            suites = []
            suite = data[1][a[i-1]:a[i]]
            case = self.data_case()[a[i-1]:a[i]]
            suites.append(suite)
            suites.append(case)
 
            allsuite.append(suites)                             
            i=i+1
        return allsuite
    
    
    def getbigsuite(self):
        i = 0
        data = self.read()
        bigsuite =[]
        test = self.data_suite()

        while i<len(data[0]):
            aa = {}
            aa.setdefault("bigsuite",data[0][i])
            aa.setdefault("suite",test[i][0])            
            aa.setdefault("cases",test[i][1])

            bigsuite.append(aa)
            i=i+1
        return bigsuite
    
       
    
    
class changetoxml:
    def __init__(self,excel,sheetname,output,filename):

        self.excel = excel 
        self.sheetname = sheetname
        self.output = output
        self.filename = filename
        
    
    def run(self):
        self.importexcel = readexcel(self.excel,self.sheetname)
        
        self.testdata = self.importexcel.getbigsuite()
        self.xml = exportxml(self.sheetname,self.testdata,self.output,self.filename)
        self.xml.export()
        

class exceloperate:   
    def __init__(self,testexcel):
        self.testexcel = testexcel   
        self.data = xlrd.open_workbook(self.testexcel)
        
    def getSheetNames(self):   
             
        return self.data.sheet_names()
    
if __name__ == "__main__":

    
    b = readexcel("D:/test.xls","Sheet1")
    
    
    c = changetoxml(u"D:/test.xls",u"Sheet1","D:/","222")
    c.run()
    
#    a =exportxml("yonghuguanlizhongxin",b.getbigsuite(),"D:/","222")
#    a.export()
