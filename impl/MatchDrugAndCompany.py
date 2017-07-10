#!/usr/bin/python3.5
# -*- coding:utf-8 -*-

import os, sys, re, time
from operator import itemgetter

from bs4 import BeautifulSoup
import jieba
import Levenshtein
import pandas as pd
import csv

from bson import ObjectId
from impl import MatchDrug
from flask import Flask, jsonify, abort, make_response, request

from impl import SearchImpl
from utils import OtherUtils, MysqlUtils, MongodbUtils, IOUtils, CollectionUtils, RegexUtils, JiebaUtils

app = Flask(__name__)


# 400页面
@app.errorhandler(400)
def not_found(error):
	return make_response(jsonify({'error': '没有接收到可用数据!(No data was received!)'}), 404)


@app.route("/")
def index():
	return "Hello, World!"


@app.route('/python/api/putlabel/drugandcompany', methods=['POST'])
def putlabel():
	# 使用Body中的x-www.form.urlencoded进行发送
	if len(request.values) < 1:
		abort(400)
	putlabeltype = 0
	if "putlabeltype" in request.values:
		putlabeltype = int(request.values["putlabeltype"])
	showdetails = False
	if "showdetails" in request.values:
		showdetails = True
	text = request.values["text"]
	result = putlabel_core(text, putlabeltype, showdetails)
	print(result)
	return jsonify(result), 200


stopwords_en_company_1 = ["corp.,ltd.", "s.a.r.l.", "co.,ltd.", "s.p.a.", "s.a.s", "corp.", "inc.", "b.v.", "n.v.",
						  "co.,", "pty.", "pte.", "a/s", "co."]
stopwords_en_company_2 = ["biopharmaceuticals", "biopharmaceutical", "pharmaceuticals", "pharmaceutical",
						  "biotechnology", "venture fund", "therapeutics", "farmaceutici", "laboratories",
						  "engineering", "laboratoire", "corporation", "biosciences", "bioscience", "biological",
						  "laboratory", "healthcare", "technology", "institutes", "institute", "biopharma", "biologics",
						  "biologic", "sciences", "ventures", "partners", "products", "medicine", "holdings", "venture",
						  "science", "biology", "biotech", "limited", "company", "medical", "health", "pharma", "group",
						  "funds", "fund", "labs", "gmbh", "kgaa", "lllp", "lab", "bio", "inc", "llp", "jsc", "aps",
						  "plc", "llc", "ltd", "ag", "kg", "lp", "oy", "sa", "bv", "ab", "nv", ""]

stopwords_zh_company_1 = ["集团股份有限公司", "股份有限责任公司", "有限责任公司", "股份有限公司", "有限公司", "制药公司", "株式会社", "研究中心", "制药厂", "西药厂",
						  "中药厂", "制品厂", "研究所", "研究院", "实验室", "公司", "药厂", "工厂", "医院"]

stopwords_zh_company_2 = ["制药", "药业", "医药", "技术", "科技", "生物"]

similar_dict = {"集团股份有限公司": {"集团股份有限公司", "股份有限责任公司", "股份有限公司"}, "股份有限责任公司": {"集团股份有限公司", "股份有限责任公司",
																			 "股份有限公司"}, "股份有限公司": {"集团股份有限公司",
																								   "股份有限责任公司",
																								   "股份有限公司"}, "有限责任公司": {
	"有限责任公司", "有限公司", "公司"}, "有限公司": {"有限责任公司", "有限公司", "公司"}, "公司": {"有限责任公司", "有限公司", "公司"}}

dict_set = []
dict_dict = {}
dict_zh = {}
dict_en = {}
exclude_set = set()
dict_drug_database = None
dict_drug_discover = None

path_zh = IOUtils.get_path_target("drugandcompany_zh.txt")
path_en = IOUtils.get_path_target("drugandcompany_en.txt")
path_set_drug_database = IOUtils.get_path_target("match_jieba_drug_exact_database.txt")
path_set_drug_discover = IOUtils.get_path_target("match_jieba_drug_exact_discover.txt")
path_set_company = IOUtils.get_path_target("drugandcompany_all_set_company.txt")
path_set = IOUtils.get_path_target("drugandcompany_all_set.txt")

path_right = IOUtils.get_path_target("drugandcompany_right.xls")
path_similar = IOUtils.get_path_target("drugandcompany_similar.xls")
path_fuzzy = IOUtils.get_path_target("drugandcompany_fuzzy.xls")
path_error = IOUtils.get_path_target("drugandcompany_error.xls")
sql_article = "select id,content from yymf_article "
# sql_article += "where id=231"

# sql_drug="select standard_name_en,full_name_en from yymf_discover_company "
sql_company = "select name,name,name_used from yymf_manufactory where is_delete <>1 "
# sql_company += "and name in ('安？？？？品') "
# sql_company += "and name like '%康美药业股份有限公司%' "
tokenizer_company = None
tokenizer_drug_database = None
tokenizer_drug_discover = None


def load_exclude():
	IOUtils.my_read(IOUtils.get_path_sources("exclude_company.txt"), exclude_set)
	IOUtils.my_read(IOUtils.get_path_sources("chinacity.txt"), exclude_set)


def preDeal(mydict, isfuzzymatch=True, isdiscover=True):
	# 遍历出来的key是用来做为value
	for value in mydict:
		keys = mydict[value]
		for key in keys:
			# 去前後空格,并按空格切割
			key = key.replace("（", "(").replace("）", ")")
			newcompany = RegexUtils.remove_diy_chars(key, "\(.*?\)")
			newcompany = RegexUtils.remove_diy_chars(newcompany, "\[.*?\]")
			if newcompany:
				companys = newcompany.replace("", " ").split("|")
			else:
				companys = key.replace("", " ").split("|")
			for company in companys:
				company = company.strip()
				if company:
					# 处理中文
					if RegexUtils.contain_zh(company):
						length = len(company)
						isremovestop = True
						# 长度小于6的不去通用停止词
						if length < 6:
							isremovestop = False
						company = RegexUtils.remove_special_chars(company, " ").strip()
						flag = True
						for city in exclude_set:
							if company in city:
								flag = False
						if flag:
							if " " not in company:
								CollectionUtils.add_dict_setvalue_single(dict_dict, company, value)
						else:
							continue
						words = company.split()
						# 去除含有特殊字符的停止词,并去除特殊字符
						if isfuzzymatch:
							if isremovestop:
								for stop in stopwords_zh_company_1:
									for index, word in enumerate(words):
										if stop in word:
											newword = word.replace(stop, "")
											if len(newword) > 2:
												words[index] = newword
											elif len(stop) == 3 and "厂" in stop:
												words[index] = word.replace("厂", "")
											# for stop in stopwords_zh_2:
											# 	for index, word in enumerate(words):
											# 		if stop in word:
											# 			newword = word.replace(stop, "")
											# 			words[index] = newword
						# 用空格连接词组
						words = [s for s in words if s]
						if words:
							newkey = " ".join(filter(lambda s: len(s) > 0, words))
							# 防止过拟合
							for city in exclude_set:
								if newkey in city:
									newkey = company
							if " " not in newkey:
								CollectionUtils.add_dict_setvalue_single(dict_dict, newkey, value)
					# 处理英文
					else:
						newwords = None
						words = company.split()
						if isfuzzymatch:
							# 去除含有特殊字符的停止词,并去除特殊字符
							for stop in stopwords_en_company_1:
								for index, word in enumerate(words):
									if stop in word:
										newword = word.replace(stop, "")
										words[index] = newword
							tempwords = []
							for word in words:
								if word:
									tempwords.extend(RegexUtils.remove_special_chars(word, " ").split())
							words = tempwords
							# 去除通用公司名称
							newwords = [w for w in words if not w in stopwords_en_company_2]
						# 用空格连接词组
						if newwords:
							newkey = " ".join(newwords)
						else:
							newkey = " ".join(filter(lambda s: len(s) > 0, words))
						CollectionUtils.add_dict_setvalue_single(dict_dict, newkey, value)


def split_dict():
	new_dict = {}
	for key in dict_dict:
		# 判断是否全部数字或者长度大于30
		if key.isdigit():
			continue
		elif RegexUtils.contain_zh(key):
			length = len(key)
			if length > 1 and length < 24:
				valset = dict_dict[key]
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
			dict_en[key] = dict_dict[key]
			new_dict[key] = dict_dict[key]
	return new_dict


def writedict(iswritedict=True, isfuzzymatch=True, isdiscover=False, readcache=True, is_read_drug=True):
	isexist = os.path.exists(path_set_company)
	if readcache and isexist:
		SearchImpl.read_cache(path_zh, dict_zh)
	else:
		# 加载排除字典
		load_exclude()
		mydict = MysqlUtils.sql_to_dict(sql_company)
		preDeal(mydict, isfuzzymatch, isdiscover)
		new_dict = split_dict()

		# 判断写入key还是写入key/value
		if iswritedict:
			zhlist = list(dict_zh.items())
			zhlist.sort(key=lambda t: len(t[0]), reverse=True)
			IOUtils.my_write(path_zh, zhlist)
		# enlist = list(dict_en.items())
		# enlist.sort(key=lambda t: len(t[0]), reverse=True)
		# IOUtils.my_write(path_en, enlist)
		else:
			ls = list(dict_zh.keys())
			ls.sort(key=lambda t: len(t), reverse=True)
			IOUtils.my_write(path_zh, ls)

		# 写入jieba字典
		set_company = set(dict_zh)
		JiebaUtils.writefile(path_set_company, set_company)

	# 写入获取药品字典
	if is_read_drug:
		global dict_drug_database, dict_drug_discover
		dict_drug_database = MatchDrug.writedict(isfuzzymatch=False, isdiscover=False, readcache=True, returntype=0)
		dict_drug_discover = MatchDrug.writedict(isfuzzymatch=False, isdiscover=True, readcache=True, returntype=0)

	# # 写入药品和公司字典
	# for drug in dict_drug:
	# 	if drug in new_dict:
	# 		coms = new_dict[drug]
	# 		drugs = dict_drug[drug]
	# 		new_dict[drug] = coms | drugs
	# 	else:
	# 		new_dict[drug] = dict_drug[drug]
	# global dict_dict
	# dict_dict = new_dict
	# global dict_set
	# dict_set = set(dict_dict.keys())
	#
	# ls = list(dict_dict.items())
	# ls.sort(key=lambda t: len(t[0]), reverse=True)
	# IOUtils.my_write(path_dict, ls)
	# JiebaUtils.writefile(path_set, dict_set)
	print("writedict over.")


def match_from_mongodb():
	MongodbUtils.set_collection("cfda_news_notify_content")
	getlist = MongodbUtils.get_list()
	# getlist = MongodbUtils.get_list({"currentTime": {"$gt": 1494664001430}})
	# getlist = MongodbUtils.get_list({"_id": ObjectId("5916bed33c95966d4b201082")})
	i = 0
	right = set()
	error = set()
	for row in getlist:
		text = row["content"]
		# 去html标签
		text = BeautifulSoup(text, "html.parser").get_text().replace("\n", "")
		# 去括号里面东西
		text = text.replace("（", "(").replace("）", ")")
		text = RegexUtils.remove_diy_chars(text, "\(.*?\)")
		text = RegexUtils.remove_diy_chars(text, "\[.*?\]")
		text = " ".join(text.split())
		keywords_drug = tokenizer_drug_database.cutwkz_set(text)
		keywords_company = tokenizer_company.cutwkz_dict(text)

		keywords = set()
		i += 1
		if keywords_drug:
			for key in keywords_drug:
				keywords.add("{0}{1} 【 药品 】".format(key, dict_drug_database[key]))
		if keywords_company:
			for key in keywords_company:
				# 匹配到公司名称超过10字的直接添加
				if len(key) > 10:
					keywords.add("{0}【 公司 】".format(key))
					continue
				# 匹配到公司名称没有超过10字,需要进行判断
				flag = False
				test = None
				for stopword in stopwords_zh_company_1:
					if stopword in key:
						flag = True
						keywords.add("{0}【 公司 】".format(key))
						break
				if not flag:
					begin = keywords_company[key][1]
					testls = RegexUtils.remove_special_chars(text[begin:begin + 10], " ").lstrip().split()
					if testls:
						test = testls[0]
						for stopword in stopwords_zh_company_1:
							if stopword in test:
								flag = True
								issim = False
								valset = dict_zh[key]
								for val in valset:
									extra = val.replace(key, "")
									if stopword in similar_dict:
										sims = similar_dict[stopword]
										if sims and extra in sims and test in sims:
											issim = True
											# keywords.add("{0}{1} 【 公司相似 】".format(key, valset))
											break
								if not issim:
									# keywords.add("{0}{1} 【 公司模糊 】".format(key, valset))
									pass
								break
		# 写入到文件中
		if keywords:
			right.add("{0}\t{1}\t{2}".format(row["_id"], text, keywords))
		else:
			error.add(text)
	IOUtils.my_write(path_error, error)
	IOUtils.my_write(path_right, right)


def match_from_mysql():
	# getlist = MongodbUtils.get_list()
	# getlist = MongodbUtils.get_list({"currentTime": {"$gt": 1494664001430}})
	# getlist = MongodbUtils.get_list({"_id": ObjectId("5916bed33c95966d4b201082")})
	getlist = MysqlUtils.getrows(sql_article)
	totalright = set()
	totalerror = set()
	totalsimilar = set()
	totalfuzzy = set()
	for row in getlist:
		id = row[0]
		txt = row[1]
		# 去html标签
		txt = BeautifulSoup(txt, "html.parser").get_text().replace("\n", "")
		# 去括号里面东西
		text = txt.replace("（", "(").replace("）", ")")
		text = RegexUtils.remove_diy_chars(text, "\(.*?\)")
		text = RegexUtils.remove_diy_chars(text, "\[.*?\]")
		text = " ".join(text.split())
		text = RegexUtils.remove_special_chars_nosplit(text)
		# keywords_company = tokenizer_company.cutwkz_dict(text)
		# keywords_drug_database = tokenizer_drug_database.cutwkz_set(text)
		keywords_drug_discover = tokenizer_drug_discover.cutwkz_set(text)

		setright = set()
		setsimilar = set()
		setfuzzy = set()
		if keywords_drug_discover:
			for key in keywords_drug_discover:
				setright.add("{0}{1} 【 发现药品 】".format(key, dict_drug_discover[key]))
		# if keywords_drug_database:
		# 	for key in keywords_drug_database:
		# 		setright.add("{0}{1} 【 药品 】".format(key, dict_drug_database[key]))
		# if keywords_company:
		# 	for key in keywords_company:
		# 		# 匹配到公司名称超过10字的直接添加
		# 		if len(key) > 10:
		# 			setright.add("{0}【 公司 】".format(key))
		# 			continue
		# 		# 匹配到公司名称没有超过10字,需要进行判断
		# 		flag = False
		# 		for stopword in stopwords_zh_company_1:
		# 			if stopword in key:
		# 				flag = True
		# 				setright.add("{0}【 公司 】".format(key))
		# 				break
		# 		if not flag:
		# 			begin = keywords_company[key][1]
		# 			testls = RegexUtils.remove_special_chars(text[begin:begin + 10]," ").lstrip().split()
		# 			if testls:
		# 				test = testls[0]
		# 				for stopword in stopwords_zh_company_1:
		# 					if stopword in test:
		# 						flag = True
		# 						issim = False
		# 						valset = dict_zh[key]
		# 						for val in valset:
		# 							extra = val.replace(key, "")
		# 							if stopword in similar_dict:
		# 								sims = similar_dict[stopword]
		# 								if sims and extra in sims and test in sims:
		# 									issim = True
		# 									setsimilar.add("{0}{1} 【 公司相似 】".format(key, valset))
		# 									break
		# 						if not issim:
		# 							setfuzzy.add("{0}{1} 【 公司模糊 】".format(key, valset))
		# 						break
		# 写入到文件中
		flag = True
		if setright:
			totalright.add("{0}\t{1}\t{2}".format(id, txt, setright))
			flag = False
		# if setsimilar:
		# 	totalsimilar.add("{0}\t{1}\t{2}".format(id, txt, setsimilar))
		# 	flag = False
		# if setfuzzy:
		# 	totalfuzzy.add("{0}\t{1}\t{2}".format(id, txt, setfuzzy))
		# 	flag = False
		if flag:
			totalerror.add("{0}\t{1}".format(id, txt))
	IOUtils.my_write(path_right, totalright)
	# IOUtils.my_write(path_similar, totalsimilar)
	# IOUtils.my_write(path_fuzzy, totalfuzzy)
	IOUtils.my_write(path_error, totalerror)


def putlabel_core(text, putlabeltype, showdetails):
	"""

	:param text:
	:param putlabeltype: 0全部,1公司,2药品
	:param showdetails:
	:return:
	"""
	if not text:
		return None
	text = BeautifulSoup(text, "html.parser").get_text().replace("\n", "")
	# 去括号里面东西
	txt = text.replace("（", "(").replace("）", ")")
	txt = RegexUtils.remove_diy_chars(txt, "\(.*?\)")
	txt = RegexUtils.remove_diy_chars(txt, "\[.*?\]")
	txt = " ".join(txt.split())
	txt = RegexUtils.remove_special_chars_nosplit(txt)
	setcompany = {}
	# setsimilar = set()
	setcompany_fuzzy = {}
	setdrug_database={}
	mapdrug_discover={}
	mapresult={}
	# 匹配公司
	if putlabeltype==0 or putlabeltype==1:
		keywords_company = tokenizer_company.cutwkz_dict(txt)
		if keywords_company:
			for key in keywords_company:
				# 匹配到公司名称超过10字的直接添加
				if len(key) > 10:
					# setcompany.add("{0}{1}".format(key, dict_zh[key]))
					setcompany[key]=list(dict_zh[key])
					continue
				# 匹配到公司名称没有超过10字,需要进行判断
				flag = False
				for stopword in stopwords_zh_company_1:
					if stopword in key:
						flag = True
						# setcompany.add("{0}{1}".format(key, dict_zh[key]))
						setcompany[key] = list(dict_zh[key])
						break
				if not flag:
					begin = keywords_company[key][1]
					testls = RegexUtils.remove_special_chars(txt[begin:begin + 10], " ").lstrip().split()
					if testls:
						test = testls[0]
						for stopword in stopwords_zh_company_1:
							if stopword in test:
								flag = True
								issim = False
								valset = dict_zh[key]
								for val in valset:
									extra = val.replace(key, "")
									if stopword in similar_dict:
										sims = similar_dict[stopword]
										if sims and extra in sims and test in sims:
											issim = True
											# setsimilar.add("{0}{1} 【 公司相似 】".format(key, valset))
											# setcompany.add("{0}{1}".format(key, valset))
											setcompany[key] = list(valset)
											break
								if not issim:
									# setcompany_fuzzy.add("{0}{1}".format(key, valset))
									setcompany_fuzzy[key]=list(valset)
								break
		mapresult["company"]=setcompany
		mapresult["company_fuzzy"]=setcompany_fuzzy
	# 匹配药品
	if putlabeltype == 0 or putlabeltype == 2:
		keywords_drug_database = tokenizer_drug_database.cutwkz_set(txt)
		keywords_drug_discover = tokenizer_drug_discover.cutwkz_set(txt)
		if keywords_drug_database:
			for key in keywords_drug_database:
				# setdrug_database.add("{0}{1}".format(key, dict_drug_database[key]))
				setdrug_database[key]=list(dict_drug_database[key])
		if keywords_drug_discover:
			for key in keywords_drug_discover:
				# mapdrug_discover.add("{0}{1}".format(key, dict_drug_discover[key]))
				mapdrug_discover[key]=list(dict_drug_discover[key])
		mapresult["drug_database"] = setdrug_database
		mapresult["drug_discover"] = mapdrug_discover
	return mapresult


if __name__ == '__main__':
	writedict(iswritedict=True, isfuzzymatch=True, isdiscover=False, readcache=True, is_read_drug=True)

	global tokenizer_company, tokenizer_drug_database, tokenizer_drug_discover
	tokenizer_company = jieba.Tokenizer(path_set_company)
	tokenizer_drug_database = jieba.Tokenizer(path_set_drug_database)
	tokenizer_drug_discover = jieba.Tokenizer(path_set_drug_discover)
	# match_from_mongodb()
	# match_from_mysql()

	# 本机只能通过127.0.0.1或者localhost可访问,其它机子只能通过192.168.2.135可以访问(默认是5000)
	app.run(host='0.0.0.0', port=5000, debug=True)
	print("\nover")
