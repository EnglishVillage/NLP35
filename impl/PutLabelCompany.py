#!/usr/bin/python3.5
# -*- coding:utf-8 -*-

import os, sys, re, time

sys.path.append('/home/esuser/NLP35')

from impl import PutLabelCore
from impl.PutLabelCore import MatchType
from utils import CollectionUtils, RegexUtils, StringUtils

stopwords_zh_company_1 = ["控股集团有限公司", "集团股份有限公司", "股份有限责任公司", "控股集团公司", "集团股份公司", "集团有限公司", "股份有限公司", "有限责任公司",
						  "控股有限公司", "股份有限公司", "集团公司", "控股集团", "股份公司", "有限公司", "控股公司", "制药公司", "株式会社", "研究中心", "制药厂",
						  "西药厂", "中药厂", "制品厂", "研究所", "研究院", "实验室", "公司", "药厂", "工厂", "医院"]
stopwords_zh_company_2 = ["制药", "药业", "医药", "技术", "科技", "生物"]
stopwords_zh_company = stopwords_zh_company_1 + stopwords_zh_company_2
stopwords_en_company_1 = ["corp.,ltd.", "co., ltd.", "co.,ltd.", "s.a.r.l.", "s.p.a.", "s.a.s", "corp.", "inc.", "b.v.",
						  "n.v.", "co.,", "pty.", "pte.", "ltd.", "a/s", "co."]
stopwords_en_company_2 = ["biopharmaceuticals", "biopharmaceutical", "pharmaceuticals", "pharmaceutical",
						  "biotechnology", "venture fund", "therapeutics", "farmaceutici", "laboratories",
						  "engineering", "laboratoire", "corporation", "biosciences", "bioscience", "biological",
						  "laboratory", "healthcare", "technology", "institutes", "institute", "biopharma", "biologics",
						  "biologic", "sciences", "ventures", "partners", "products", "medicine", "holdings", "venture",
						  "science", "biology", "biotech", "limited", "company", "medical", "health", "pharma", "group",
						  "funds", "fund", "labs", "gmbh", "kgaa", "lllp", "lab", "bio", "inc", "llp", "jsc", "aps",
						  "plc", "llc", "ltd", "ag", "kg", "lp", "oy", "sa", "bv", "ab", "nv"]
# similar_dict = {"集团股份有限公司": {"集团股份有限公司", "股份有限责任公司", "股份有限公司"}, "股份有限责任公司": {"集团股份有限公司", "股份有限责任公司",
# 																			 "股份有限公司"}, "股份有限公司": {"集团股份有限公司",
# 																								   "股份有限责任公司",
# 																								   "股份有限公司"}, "有限责任公司": {
# 	"有限责任公司", "有限公司", "公司"}, "有限公司": {"有限责任公司", "有限公司", "公司"}, "公司": {"有限责任公司", "有限公司", "公司"}}
# companylogogram = {"inc", "ltd", "llc", "plc", "corp", "co,ltd", "co, ltd", "集团股份有限公司", "股份有限责任公司", "有限责任公司", "股份有限公司",
# 				   "有限公司", "制药公司", "株式会社", "公司"}
# 这里去掉了.
companylogogram = ["控股集团有限公司", "集团股份有限公司", "股份有限责任公司", "co, ltd", "co,ltd", "集团股份公司", "集团有限公司", "股份有限公司", "有限责任公司",
				   "控股有限公司", "股份有限公司", "corp", "集团公司", "控股集团", "股份公司", "有限公司", "控股公司", "制药公司", "株式会社", "inc", "ltd",
				   "llc", "plc", "公司"]

sql_discover_list = [
	"select code,full_name_cn,full_name_en,standard_name_cn,standard_name_en from yymf_discover_company "]
sql_discover_where = "where is_delete <>1 "
# sql_discover_where += 'and id=1994 '
# sql_discover_where += "and code in ('C000001','C000002')"
sql_database_list = ["select name,name_used from yymf_manufactory "]
sql_database_where = "where is_delete <>1 "


def preDeal_core(key, exclude_set):
	# 去前後空格
	key = StringUtils.remove_parentheses(key)
	# 处理中文
	if RegexUtils.contain_zh(key):
		key = RegexUtils.get_word_nospecial_withspace(key)
		# 防止过拟合
		if key in exclude_set:
			return None
		isremovestop = True
		# 长度小于6的不去通用停止词
		length = len(key)
		if length < 6:
			isremovestop = False
		# 去除含有特殊字符的停止词,并去除特殊字符
		if isremovestop:
			newcompany = key
			for stop in stopwords_zh_company_1:
				if stop in newcompany:
					newword = newcompany.replace(stop, "")
					# 判断是否长度大于2,如果不大于2直接替换掉厂
					if len(newword) > 2:
						if newword in exclude_set:
							break
						else:
							newcompany = newword
					else:
						if len(stop) == 3 and "厂" in stop:
							newword = newcompany.replace("厂", "")
							if newword in exclude_set:
								break
							else:
								newcompany = newword
			if newcompany:
				key = newcompany
		return key
	# 处理英文
	else:
		newword = key
		# 去除含有特殊字符的停止词,并去除特殊字符
		for stop in stopwords_en_company_1:
			newword = newword.replace(stop, "")
		if newword:
			key = newword
		# 去除特殊字符
		key = RegexUtils.get_english_nospecial(key)
		# 去除通用公司名称
		newwords = " ".join((w for w in key.split() if not w in stopwords_en_company_2))
		if newwords:
			key = newwords
		return key


def preDeal_database(rows, dict_all, isfuzzymatch, exclude_set):
	# 遍历出来的key是用来做为value
	for row in rows:
		value = row[0].strip()
		if value:
			for i in range(1, len(row)):
				keys = StringUtils.strip_and_lower_split_single(row[i], "|")
				for key in keys:
					key = preDeal_core(key, exclude_set)
					CollectionUtils.add_dict_setvalue_single(dict_all, key, value)


def preDeal_discover(rows, dict_all, isfuzzymatch, exclude_set):
	# 遍历出来的key是用来做为value
	valueother = set()
	for row in rows:
		value = row[0].strip()
		if value:
			valueother.clear()
			for i in range(1, len(row)):
				key = StringUtils.strip_and_lower(row[i])
				if key:
					valueother.add(key)
					key = preDeal_core(key, exclude_set)
					if key:
						valueother.add(key)
			value = (value, tuple(valueother))
			for key in valueother:
				CollectionUtils.add_dict_setvalue_single(dict_all, key, value)


def split_dict(dict_all, dict_zh, dict_en, isfuzzymatch):
	new_dict = {}
	for key in dict_all:
		# 判断是否全部数字或者长度大于30
		if key.isdigit():
			continue
		elif RegexUtils.contain_zh(key):
			length = len(key)
			if length > 2 and length < 24:
				valset = dict_all[key]
				dict_zh[key] = valset
				new_dict[key] = valset
			# if length == 3 and len(valset) == 1:
			# 	flag = False
			# 	for val in valset:
			# 		if val == key:
			# 			flag = True
			# 		break
			# 	if flag:
			# 		continue
			# dict_zh[key] = valset
			# new_dict[key] = valset
		elif len(key) > 1:
			dict_en[key] = dict_all[key]
			new_dict[key] = dict_all[key]
	return new_dict


def writedict(isdiscover=True, iswritedict=True, isfuzzymatch=False, readcache=False, returntype=0):
	return PutLabelCore.writedict(MatchType.company, ("exclude_company.txt", "chinacity.txt"),
								  [sql + sql_discover_where for sql in sql_discover_list], preDeal_discover,
								  [sql + sql_database_where for sql in sql_database_list], preDeal_database, split_dict,
								  None, None, isdiscover=isdiscover, iswritedict=iswritedict, isfuzzymatch=isfuzzymatch,
								  readcache=readcache, returntype=returntype)


if __name__ == '__main__':
	readcache = False
	dict_database_company, jieba_dict_database_company = writedict(isdiscover=False, readcache=readcache)
	# dict_discover_company, jieba_dict_discover_company = writedict(isdiscover=True, readcache=readcache)
	print("over")
