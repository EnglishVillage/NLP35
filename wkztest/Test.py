#!/usr/bin/python
# -*- coding:utf-8 -*-


import os, sys, re, time
import pandas as pd
import numpy as np
from collections import OrderedDict, MutableSet
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
from gensim.models import Word2Vec
from sklearn.naive_bayes import GaussianNB as GNB
from sklearn.ensemble import RandomForestClassifier

try:
	import json  # python >= 2.6
except ImportError:
	import simplejson as json  # python <= 2.5

# 导入自定义的包
sys.path.append(os.path.join(".", "utils"))
from utils import OtherUtils, MysqlUtils, TableUtils

# s=re.sub("(.+)","","吸附手足口病(ev71型、ca16型)双价灭活疫苗(vero细胞)")
# # s=re.findall("(.+?)","吸附手足口病(ev71型、ca16型)双价灭活疫苗(vero细胞)")
# print(s)

# url = 'https://113.215.20.136:9011/113.215.6.77/c3pr90ntcya0/youku/6981496DC9913B8321BFE4A4E73/0300010E0C51F10D86F80703BAF2B1ADC67C80-E0F6-4FF8-B570-7DC5603F9F40.flv'
# pattern = 'http://(.*?):9011/'
# out = re.sub(pattern, 'http://127.0.0.1:9091/', url)
# print(out)
# ('maposhangfengmianyiqiudanbai2', {"马破伤风免疫球蛋白(F(ab')2)"})
# ('mpsfmyqdb2', {"马破伤风免疫球蛋白(F(ab')2)"})
# ('马破伤风免疫球蛋白2', {"马破伤风免疫球蛋白(F(ab')2)"})
# aa = (["氟伏沙明", "洛索洛芬", "磷酸"], 0.9155555555555556, 0, 0)
# if len(aa[0])>1:
# 	for v in aa[0]:
# 		print((v,aa[1],aa[2],aa[3]))
# else:
# 	print((aa[0],aa[1],aa[2],aa[3]))

OrderedDict()

fuzzy_set={"c","s","z","f","l","r","an","en","in","ian","uan"}

fuzzy_set.add(1)
print(fuzzy_set)

