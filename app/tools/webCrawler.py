'''
Created on 2015年8月20日

@author: wangxun
'''
import httplib2
from bs4 import BeautifulSoup

h = httplib2.Http(".cache")  
url = 'http://vipreader.qidian.com/BookReader/BuyVIPChapterList.aspx?BookId=3446747'
resp, content = h.request(url, "GET") 
content = str(content,encoding = "utf-8")
soup = BeautifulSoup(content)

print(soup.find_all('td'))


file = open('D:/webdata.text','a',encoding = "utf-8")
#file.write(content)
file.close()
print(resp)