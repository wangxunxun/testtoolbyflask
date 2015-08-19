'''
Created on 2015年8月19日

@author: xun
'''
import httplib2  
from urllib.parse import urlencode
import json
h = httplib2.Http(".cache")  

data = dict(email = 2443, username="Atesco443333mmen33t",password = '1234')
encodedjson = json.dumps(data)
 
resp, content = h.request("http://127.0.0.1:5000/api/v1.0/users/", "POST",encodedjson, headers={"Content-Type": "application/json"} )  

print(resp)
print(content)