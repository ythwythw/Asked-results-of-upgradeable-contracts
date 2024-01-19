import pandas as pd
import os
import csv
import re
import json
import string
from tqdm import tqdm

def findfun(line):
   t = line.strip()
   ret1 = re.match('^(function)[(\w)|( )]*?(\{)', t)
   ret2 = re.match('^(function)[(\w)|( )]*?(\()', t)
   result = (ret1 == None) and (ret2 == None)
   if result:
      return False
   else:
      return True

def FindFun(code, h):
   t = code
   loc = 0
   end = t.find('\n')
   temp = ''
   while True:
        if findfun(t[loc:end]):
            temp = t[loc:end]
        
        loc = end + 1
        if loc>h:
            return temp
        end = t.find('\n', loc + 1)   
        # if end == -1:
        #     break

def address_in_delegatecall(code):
    positions = find_all(code, 'delegatecall(')
    for h in positions:
        t = code.find('(', h) + 1
        f = 1
        while f!=0:
            if code[t] == '(':
                f += 1
            elif code[t] == ')':
                f += -1
            t += 1
        if code[h:t].find(',') != -1:
            address = code[h:t].split(',')[1].strip()
            return address, h
    # return code[h:t]
    return 0

def external_or_internal(code, h):
    fun = FindFun(code, h)
    if fun.find('internal') != -1:
        return fun, 0
    return fun, 1

def find_all(string, sub):
    start = 0
    pos = []
    while True:
        start = string.find(sub, start)
        if start == -1:
            return pos
        pos.append(start)
        start += len(sub)


def isUp(code):
    punc = string.punctuation
    if address_in_delegatecall(code) != 0:
        address, h = address_in_delegatecall(code)
        fun, f = external_or_internal(code, h)
        if f == 0:
            #internal 
            fun = fun.strip()
            fName = fun.split(' ')[1].split('(')[0]
            positions = find_all(code, fName)
            content = []
            for p in positions:
                t = code.find('(', p) + 1
                f = 1
                while f!= 0:
                    if code[t] == '(':
                        f += 1
                    elif code[t] == ')':
                        f += -1
                    t += 1
                content.append(code[p:t])
            for term in content:
                if term not in punc:
                    if len(find_all(term, '('))>1:
                        if code.find('sload') != -1 and code.find('sstore') != -1:
                            return 1
        else:
            #external
            if address.find('(') == -1:
                positions = find_all(code, address)
                content = []
                for p in positions:
                    if '=' in code[p-2:p]:
                        temp = code[p-50:p].split(' ')[-3]
                        if temp not in punc:
                            content.append(temp)
                    if '=' in code[p:p+len(address)+2]:
                        temp = code[p:p+50].split(' ')[2]
                        if temp not in punc:
                            content.append(temp)
                for term in content:
                    if len(find_all(code, term))>1:
                        return 1
            else:
                if address.find('sload') != -1:
                    address = address.split('(')[1].split(')')[0]
                    return 1
            
    return 0

dele_fram = pd.read_csv('../data2/delegateCall/deleFram.csv')

all_up = []
all_no = []
# proxy_up['method'] = ''
# for i, code in enumerate(proxy_up['code']):
for i, term in tqdm(dele_fram.iterrows(), total=len(dele_fram)):
    code = term['code']
    if type(code) != float:
        code = code.replace('\\n', '\n')
        f = isUp(code)
        if f == 1:
            all_up.append(term['fromAddress'])
        elif f == 0:
            all_no.append(term['fromAddress'])
print(len(all_up), len(all_no))

