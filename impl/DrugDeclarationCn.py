#!/usr/bin/python3.5
# -*- coding:utf-8 -*-

"""
	静姐,对发现药品字典中国内申报名进行精确匹配
"""

import os, sys, re, time

sys.path.append('/home/esuser/NLP35')
from utils import IOUtils, TableUtils
from utils.Utils import MysqlUtils

mysql_utils = MysqlUtils()
mydict = {}
# rowsdict = mysql_utils.getrows("select id,standard_name,alternative_name from yymf_drugs_name_dic")
rowsdict = mysql_utils.getrows(
	"select id,standard_name,alternative_name,alternative_inn,alternative_active_ingredient_name,trade_name,investigational_code from yymf_drugs_name_dic")
for t in rowsdict:
	val = "%s:%s" % (t[0], t[1].lstrip())
	for i in range(2, len(t)):
		if t[i]:
			t2 = t[i].lstrip().lower()
			if t2:
				ls = t2.split("|")
				for key in ls:
					mydict[key.lstrip()] = val

name = "发现-国内申报名20170719"
name = "发现-无剂型20170719"
rows = TableUtils.read_xlsx(IOUtils.get_path_sources(name + ".xlsx"), istitle=True)
for ls in rows:
	myset = set()
	for i in range(2, len(ls)):
		val = ls[i]
		if val:
			if type(val) == str:
				val = val.lstrip().lower()
			else:
				val = str(val).lstrip().lower()
			if val:
				drugs = val.replace("；", ";").split(";")
				for drug in drugs:
					myset.add(drug.lstrip())
	flag = True
	if myset:
		for drug in myset:
			if drug in mydict:
				flag = False
				ls.append(mydict[drug])
				break
	if flag:
		ls.append(0)

TableUtils.write_xlsx(IOUtils.get_path_target(name + "结果.xlsx"), rows)
