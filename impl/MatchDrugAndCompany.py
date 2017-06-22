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

from impl import SearchImpl
from flask import Flask, jsonify, abort, make_response, request
from utils import OtherUtils, MysqlUtils, MongodbUtils, IOUtils, CollectionUtils, RegexUtils, JiebaUtils

app = Flask(__name__)


# 400页面
@app.errorhandler(400)
def not_found(error):
	return make_response(jsonify({'error': '没有接收到可用数据!(No data was received!)'}), 404)


@app.route("/")
def index():
	return "Hello, World!"


@app.route('/python/api/search/drugandcompany', methods=['POST'])
def search():
	# # 使用Body中的x-www.form.urlencoded进行发送
	# if len(request.values) < 1:
	# 	abort(400)
	# text = request.values["text"]
	# if "showdetails" in request.values:
	# 	result = search_debug_details(text)
	# else:
	# 	result = search_debug_details(text, False)
	# return jsonify({'match': result}), 200
	pass


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
stopwords_zh_company_1 = ["股份有限公司", "有限责任公司", "有限公司", "制药公司", "研究中心", "株式会社", "制药厂", "制品厂", "研究所", "研究院", "实验室", "中药厂",
						  "西药厂", "药厂", "公司", "医院", "工厂", "制药", "药业"]
stopwords_zh_company_2 = ["医药", "技术", "科技", "生物"]

dict_set = []
dict_dict = {}
dict_zh = {}
dict_en = {}
exclude_set = set()
dict_drug = None
set_drug = None

path_zh = IOUtils.get_path_target("drugandcompany_zh.txt")
path_en = IOUtils.get_path_target("drugandcompany_en.txt")
path_set_drug = IOUtils.get_path_target("drugandcompany_all_set_drug.txt")
path_set_company = IOUtils.get_path_target("drugandcompany_all_set_company.txt")
path_set = IOUtils.get_path_target("drugandcompany_all_set.txt")

path_right = IOUtils.get_path_target("drugandcompany_right.xls")
path_error = IOUtils.get_path_target("drugandcompany_error.xls")

# sql_drug="select standard_name_en,full_name_en from yymf_discover_company "
sql_company = "select name,name,name_used from yymf_manufactory "
# sql_company += "where name in ('赛普敦') "
tokenizer_company = None
tokenizer_drug = None


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
			newcompany = re.sub(r"\(.*?\)", "", key)
			newcompany = re.sub(r"\[.*?\]", "", newcompany)
			if newcompany:
				companys = newcompany.replace("", " ").split("|")
			else:
				companys = key.replace("", " ").split("|")
			for company in companys:
				company = company.strip()
				if company:
					# 处理中文
					if RegexUtils.contain_zh(company):
						company = re.sub(RegexUtils.special_chars, " ", company).strip()
						flag = True
						for city in exclude_set:
							if company in city:
								flag = False
						if flag:
							CollectionUtils.add_dict_setvalue_single(dict_dict, company, value)
						else:
							continue
						words = company.split()
						# words = ["有限公司","a"]
						# 去除含有特殊字符的停止词,并去除特殊字符
						if isfuzzymatch:
							for stop in stopwords_zh_company_1:
								for index, word in enumerate(words):
									if stop in word:
										newword = word.replace(stop, "")
										words[index] = newword
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
									tempwords.extend(re.sub(RegexUtils.special_chars, " ", word).split())
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
				if length == 3 and len(valset) == 1:
					flag = False
					for val in valset:
						if val == key:
							flag = True
						break
					if flag:
						continue
				dict_zh[key] = valset
				new_dict[key] = valset
		elif len(key) > 1:
			dict_en[key] = dict_dict[key]
			new_dict[key] = dict_dict[key]
	return new_dict


def read_cache(path, mydict):
	with open(path, "r", encoding="utf-8") as f:
		for line in f.readlines():
			if line:
				# if "阿莫西林'" in line:
				# 	print(line)
				# line = line.lstrip("('").rstrip("'})\n")
				line = line[2:-4]
				ls = line.split("', {'")
				try:
					mydict[ls[0]] = set(ls[1].split("', '"))
				except:
					ls = line.lstrip("('").rstrip("\"})\n").split("', {\"")
					mydict[ls[0]] = set(ls[1].split("\", \""))


def writedict(isfuzzymatch=True, isdiscover=True, readcache=True, is_read_drug=True):
	isexist = os.path.exists(path_set_company)
	if readcache and isexist:
		read_cache(path_zh, dict_zh)
	else:
		# 加载排除字典
		load_exclude()
		mydict = MysqlUtils.sql_to_dict(sql_company)
		preDeal(mydict, isfuzzymatch, isdiscover)
		new_dict = split_dict()

		# 只写key
		# ls=list(dict_dict.keys())
		# ls.sort(key=lambda t: len(t), reverse=True)
		# IOUtils.my_write(path_dict, ls)
		# 写key,value
		# enlist = list(dict_en.items())
		# enlist.sort(key=lambda t: len(t[0]), reverse=True)
		# IOUtils.my_write(path_en, enlist)
		zhlist = list(dict_zh.items())
		zhlist.sort(key=lambda t: len(t[0]), reverse=True)
		IOUtils.my_write(path_zh, zhlist)
		# 写入jieba字典
		set_company = set(dict_zh)
		JiebaUtils.writefile(path_set_company, set_company)

		# 写入获取药品字典
		if is_read_drug:
			global dict_drug
			global set_drug
			dict_drug = SearchImpl.writedict(isfuzzymatch=False, isdiscover=False, readcache=True, returntype=1)
			set_drug = set(dict_drug.keys())
			JiebaUtils.writefile(path_set_drug, set_drug)

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

		print("writedict")


def match_company(text):
	# 去html标签
	text = BeautifulSoup(text, "html.parser").get_text().replace("\n", "")
	# 去括号里面东西
	text = text.replace("（", "(").replace("）", ")")
	text = re.sub(r"\(.*?\)", "", text)
	text = re.sub(r"\[.*?\]", "", text)
	print([w for w in tokenizer_all.cut(text)])


def matchfrommongodb():
	MongodbUtils.set_collection("cfda_news_notify_content")
	getlist = MongodbUtils.get_list()
	# getlist = MongodbUtils.get_list({"currentTime": {"$gt": 1494664001430}})
	# getlist = MongodbUtils.get_list({"_id": ObjectId("5916c2bd3c95966d4b201a68")})
	i = 0
	right = set()
	error = set()
	for row in getlist:
		text = row["content"]
		# 去html标签
		text = BeautifulSoup(text, "html.parser").get_text().replace("\n", "")
		# 去括号里面东西
		text = text.replace("（", "(").replace("）", ")")
		text = re.sub(r"\(.*?\)", "", text)
		text = re.sub(r"\[.*?\]", "", text)

		# match_company(text)
		# break
		text = " ".join(text.split())
		keywords_drug = tokenizer_drug.cutwkz_set(text)
		keywords_company = tokenizer_company.cutwkz_dict(text)

		keywords = set()
		i += 1
		if keywords_drug:
			# keywords = keywords | keywords_drug
			for key in keywords_drug:
				keywords.add(key + " 【 药品 】")
		if keywords_company:
			for key in keywords_company:
				# 匹配到公司名称超过10字的直接添加
				if len(key) > 10:
					keywords.add(key + " 【 公司 】")
					continue
				# 匹配到公司名称没有超过10字,需要进行判断
				flag = False
				test = None
				for stopword in stopwords_zh_company_1:
					if stopword in key:
						flag = True
						keywords.add(key + " 【 公司 】")
						break
				if not flag:
					begin = keywords_company[key][1]
					testls = re.sub(RegexUtils.special_chars, " ", text[begin:begin + 10]).lstrip().split()
					if testls:
						test = testls[0]
						for stopword in stopwords_zh_company_1:
							if stopword in test:
								valset = dict_zh[key]
								for val in valset:
									if stopword in val:
										flag = True
										keywords.add(key + " 【 公司模糊 】")
										break
								if flag:
									break
				if not flag:
					pass
				# print(key+":"+test)
				# keywords.add(" 【 匹配不到 】 {0}:{1}".format(key,test))
		# 写入到文件中
		if keywords:
			right.add("{0}\t{1}\t{2}".format(row["_id"], text, keywords))
		# print(keywords_company)
		# text = ""
		# right.add("{0}\t{1}".format(row["_id"], keywordsset))
		else:
			error.add(text)
		# if i > 100:
		# 	break
	IOUtils.my_write(path_error, error)
	IOUtils.my_write(path_right, right)


if __name__ == '__main__':
	writedict(isfuzzymatch=True, isdiscover=False, readcache=True, is_read_drug=True)

	global tokenizer_company, tokenizer_drug
	tokenizer_company = jieba.Tokenizer(path_set_company)
	tokenizer_drug = jieba.Tokenizer(path_set_drug)
	matchfrommongodb()

	# 本机只能通过127.0.0.1或者localhost可访问,其它机子只能通过192.168.2.135可以访问(默认是5000)
	# app.run(host='0.0.0.0', port=5000, debug=True)
	print("\nover")
