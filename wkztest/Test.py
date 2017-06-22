#!/usr/bin/python3.5
# -*- coding:utf-8 -*-


import os, sys, re, time,math
import operator
from operator import itemgetter

import pandas as pd
import numpy as np
from collections import OrderedDict, MutableSet

from functools import reduce
from bs4 import BeautifulSoup
from sklearn.naive_bayes import MultinomialNB as MNB
from sklearn.cross_validation import cross_val_score
from sklearn.linear_model import LogisticRegression as LR
from sklearn.grid_search import GridSearchCV
import gensim
import nltk
from nltk.corpus import stopwords
import pickle
import csv
import Levenshtein
import pypinyin
from gensim.models import Word2Vec
from sklearn.naive_bayes import GaussianNB as GNB
from sklearn.ensemble import RandomForestClassifier

try:
	import json  # python >= 2.6
except ImportError:
	import simplejson as json  # python <= 2.5

# 导入自定义的包
# sys.path.append(os.path.join(".", "utils"))
from utils import OtherUtils, MysqlUtils, MongodbUtils, IOUtils, CollectionUtils, RegexUtils

myset = {"普利", "地平", "哌唑"}
mytuple = ("aa", myset)
myls = ["普利", "地平", "哌唑", "列汀", "列酮", "那非", "特罗", "溴铵", "单抗", "西普", "夫定", "膦酸", "膦酸钠", "西林", "霉素", "沙班", "西坦", "司特",
		"沙坦", "洛韦", "培南", "泊帕", "那肽", "他汀", "替尼", "噻嗪", "溴索", "特罗", "格雷", "福韦"]
mydict = {"a": {1, 2}, "b": 2, "c": 3}
mydict2 = {"a": {3, 4}, "bb": 2, "cc": 2}
mydict3 = {"aa": {3, 4}, "bb": 3, "cc": 3}
keys = mydict.keys()
ls = list(keys)

#"a": {1, 2}, "b": 2, "c": 3,"bb": 2,"cc": 2,"aa": {3, 4},

print(set(mydict.keys()))

myls.extend("".split())
print(myls)


# myls.append(map(float,"230.1,23.2,12.4".split(",")))
# print(myls)
# print(math.ceil(3/2))


# for s in ls:
# 	newstr1 = pypinyin.slug(s, separator="")
# 	newstr = pypinyin.slug(s, separator="", style=pypinyin.FIRST_LETTER)
# 	print(s+":"+newstr1+":"+newstr)

# print(IOUtils.get_path_sources_absolute("产品规格.mdb"))



# myset=set()
# for m in totalnomatch:
# 	myset.add(m[0])


# ls = line.split("', {'")
# try:
# 	aa=set(ls[1].split("', '"))
# except:
# 	ls = line.lstrip("('").rstrip("\"})\n").split("', {\"")
# 	aa=set(ls[1].split("\", \""))
# print(1)
