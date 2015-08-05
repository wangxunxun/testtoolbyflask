'''
Created on 2015年8月4日

@author: xun
'''


def compare(a,b):
    i = 0
    result = []
    while i<len(a):
        if a[i] not in b:
            result.append(a[i])            
        i = i+1
    if result ==[]:
        return True
    else:
        return result
            