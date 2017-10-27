#!/usr/bin/python3.5
# -*- coding:utf-8 -*-
import copy
import os, sys, re, time

import math
from collections import OrderedDict
from operator import add

import Levenshtein
import jieba

from impl import PutLabelCompany
from utils import CSVUtils
from utils import IOUtils
from utils import RegexUtils
from utils import StringUtils

sys.path.append('/home/esuser/NLP35')
import numpy as np
import pandas as pd

try:
	import json  # python >= 2.6
except ImportError:
	import simplejson as json  # python <= 2.5
from utils.Utils import MysqlUtils, MongodbUtils

try:
	import cPickle as pickle  # 序列化
except ImportError:
	import pickle

mysql_utils = MysqlUtils()

bound = 0.14

myset = {"普利", "地平", "哌唑"}
mytuple = ("aa", myset)
myls = ["普利", "地平", "哌唑", "列汀", "列酮", "那非", "特罗", "溴铵", "单抗", "西普", "夫定", "膦酸", "膦酸钠", "西林", "霉素", "沙班", "西坦", "司特",
		"沙坦", "洛韦", "培南", "泊帕", "那肽", "他汀", "替尼", "噻嗪", "溴索", "特罗", "格雷", "福韦"]
myls2 = [1, 2, 3, [3, 4, 5]]
mydict = {"b": 22, "c": 33, "a": [1, 2, 3]}
mydict2 = {"b": 2, "c": 3, "a": {1: "aa", 2: "bb"}}
# myls=[]
# myls.append(mydict)
# myls.append(mydict2)
# print(myls)
# aaaa = set(myls)
# print(aaaa)

if "地平a" not in myls:
	print(111111)

key = "华兰生物工程有限公司"
valuesdesc = ["华兰生物工程股份有限公司", "华兰生物工程重庆有限公司"]
setvalues = {}

# mysql_utils = MongodbUtils("clinicaltrials_gov_detail", host="60.205.151.191")
# page = mysql_utils.get_page(None, pagesize=100)
# flag=True
# names=None
# for row in page:
# 	names=row.keys()
# 	break
# CSVUtils.write_dict(IOUtils.get_path_target("clinicaltrials_gov_detail.csv"),names,page)




# df = pd.DataFrame([['GD', 'GX', 'FJ'], ['SD', 'SX', 'BJ'], ['HN', 'HB', 'AH'], ['HEN', 'HEN', 'HLJ'], ['SH', 'TJ', 'CQ']],
# columns=['p1', 'p2', 'p3'])
# print(df[1])

# txt="a()sd[f](s+d/fa)b123ABC一地工在b(d<d>)b{b}b"
# match = re.findall("【.*?】", aa)
# match = re.search("\(.*?\)", aa)
# print(match)

# aa=RegexUtils.replace_diy_chars(aa, "[a-zA-Z0-9\u4E00-\u9FD5]+", " ")
# print(aa)


aa="a()sdf(sdfa)bb(dd)bb(sdfa)(bzz)"
# aa="adasdfs"
match = re.findall("\(.*?\)", aa)
print(match)
begin=0
for m in match:
	index=aa.index(m,begin)
	if begin<index:
		print(aa[begin:index])
	print(m)
	begin=index+len(m)
	# print(begin)
if begin <len(aa):
	print(aa[begin:])
# print(match)


