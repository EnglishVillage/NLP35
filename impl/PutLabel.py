#!/usr/bin/python3.5
# -*- coding:utf-8 -*-
"""
	打标签功能
"""
import os, sys, re, time
from collections import OrderedDict

import Levenshtein

sys.path.append('/home/esuser/NLP35')

import jieba
from bs4 import BeautifulSoup
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from flask import Flask, jsonify, abort, make_response, request

from impl import PutLabelDrug, PutLabelCompany, PutLabelIndication, PutLabelTarget
from utils import RegexUtils

app = Flask(__name__)


# 400页面
@app.errorhandler(400)
def not_found(error):
	return make_response(jsonify({'error': '没有接收到可用数据!(No data was received!)'}), 404)


@app.route("/")
def index():
	return "Hello, World!"


@app.route('/python/api/putlabel', methods=['POST'])
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
	# print(result)
	return jsonify(result), 200


dict_discover_indication = None
dict_discover_target = None
dict_database_drug = None
dict_discover_drug = None
dict_database_company = None
dict_discover_company = None

tokenizer_database_drug = None
tokenizer_discover_drug = None
tokenizer_database_company = None
tokenizer_discover_company = None
tokenizer_discover_indication = None
tokenizer_discover_target = None
# 时间格式
ISOTIMEFORMAT = "%Y-%m-%d %X"
bound = 0.14


def match_drug_discover(beginindex, key, mydict, setvalues, txt):
	values = list(mydict[key])
	if len(values) > 1:
		for tuple in values:
			for value in tuple[1]:
				txtmatch = txt[beginindex:beginindex + len(value)]
				if value.lower() == txtmatch:
					setvalues[key] = [tuple[0]]
					return
		# 判断是否有单纯包含关系
		for tuple in values:
			for value in tuple[1]:
				if key in value.lower():
					setvalues[key] = [tuple[0]]
					return
		# 这里选出最好的那个
		lastwinkler = 0
		lastvalue = None
		for tuple in values:
			for value in tuple[1]:
				winkler = Levenshtein.jaro_winkler(value.lower(), key, bound)
				if winkler > 0.8 and winkler > lastwinkler:
					lastwinkler = winkler
					lastvalue = tuple[0]
		# 判断最後有没有匹配到
		if lastvalue:
			setvalues[key] = [lastvalue]
		else:
			setvalues[key] = [w[0] for w in values]
	else:
		setvalues[key] = [values[0][0]]


def match_drug_database(beginindex, key, mydict, setvalues, txt):
	values = list(mydict[key])
	if len(values) > 1:
		# 按长度降序
		values.sort(key=len, reverse=True)
		valueslower = OrderedDict()
		for value in values:
			txtmatch = txt[beginindex:beginindex + len(value)]
			lower = value.lower()
			if lower == txtmatch:
				setvalues[key] = [value]
				return
			valueslower[lower] = value
		# 判断是否有单纯包含关系
		valueslowerasc = sorted(valueslower.keys(), key=len)
		for lower in valueslowerasc:
			if key in lower:
				setvalues[key] = [valueslower[lower]]
				return
		# 这里选出最好的那个
		lastwinkler = 0
		lastvalue = None
		for lower in valueslowerasc:
			winkler = Levenshtein.jaro_winkler(lower, key, bound)
			if winkler > 0.8 and winkler > lastwinkler:
				lastwinkler = winkler
				lastvalue = valueslower[lower]
		# 判断最後有没有匹配到
		if lastvalue:
			setvalues[key] = [lastvalue]
		else:
			setvalues[key] = values
	else:
		setvalues[key] = values


def match_company_database(beginindex, key, mydict, setvalues, txt):
	values = list(mydict[key])
	if len(values) > 1:
		# 按长度降序
		valuesdesc = sorted(values, key=len, reverse=True)
		valueslower = OrderedDict()
		# 判断是否相等
		for value in valuesdesc:
			txtmatch = txt[beginindex:beginindex + len(value)]
			lower = value.lower()
			if lower == txtmatch:
				setvalues[key] = [value]
				return
			valueslower[lower] = value
		# key按长度进行升序
		valueslowerasc = sorted(valueslower.keys(), key=len)
		# 判断key和value是否有包含关系
		for lower in valueslowerasc:
			replace = lower.replace(key, "").replace(".", "").strip()
			# 判断是否相等
			if not replace:
				setvalues[key] = [valueslower[lower]]
				return
			else:
				for logogram in PutLabelCompany.companylogogram:
					if replace == logogram:
						setvalues[key] = [valueslower[lower]]
						return
		# 判断key和value是否都有包含通用公司部分
		newkey = key
		for logogram in PutLabelCompany.companylogogram:
			if logogram in key:
				newkey = key.replace(logogram, "").strip()
				break
		for value in valuesdesc:
			for logogram in PutLabelCompany.companylogogram:
				if logogram in value:
					newvalue = value.replace(logogram, "").strip()
					if newkey == newvalue:
						setvalues[key] = [value]
						return
		# 判断是否有单纯包含关系
		for lower in valueslowerasc:
			if key in lower:
				setvalues[key] = [valueslower[lower]]
				return
		# 最後还是没有匹配到
		setvalues[key] = valuesdesc
	else:
		setvalues[key] = values


def match_company_discover(beginindex, key, mydict, setvalues, txt):
	values = list(mydict[key])
	if len(values) > 1:
		for tuple in values:
			for value in tuple[1]:
				txtmatch = txt[beginindex:beginindex + len(value)]
				if value.lower() == txtmatch:
					setvalues[key] = [tuple[0]]
					return
		# 判断key和value是否有单纯包含关系
		for tuple in values:
			for value in tuple[1]:
				if key in value.lower():
					setvalues[key] = [tuple[0]]
					return
		# 判断key和value是否有包含关系(含有通用公司部分)
		for tuple in values:
			for value in tuple[1]:
				replace = value.lower().replace(key, "").replace(".", "").strip()
				if not replace:
					setvalues[key] = [tuple[0]]
					return
				else:
					for logogram in PutLabelCompany.companylogogram:
						if replace == logogram:
							setvalues[key] = [tuple[0]]
							return
		# 判断key和value是否都有包含通用公司部分
		newkey = key
		for logogram in PutLabelCompany.companylogogram:
			if logogram in key:
				newkey = key.replace(logogram, "").strip()
				break
		for tuple in values:
			for value in tuple[1]:
				value = value.lower()
				for logogram in PutLabelCompany.companylogogram:
					if logogram in value:
						newvalue = value.replace(logogram, "").strip()
						if newkey == newvalue:
							setvalues[key] = [tuple[0]]
							return
		# 最後还是没有匹配到
		setvalues[key] = [w[0] for w in values]
	else:
		setvalues[key] = [values[0][0]]


def match_company(txt, tokenizer, mydict, mapresult, matchtype, func):
	setvalues = {}
	keywords = tokenizer.cutwkz_dict(txt)
	if keywords:
		for key in keywords:
			beginindex = keywords[key][0]
			# 匹配到公司名称超过10字的直接添加
			if len(key) > 10:
				func(beginindex, key, mydict, setvalues, txt)
				continue
			# 匹配到公司名称没有超过10字,需要进行判断
			if RegexUtils.contain_zh(key):
				flag = True
				for stopword in PutLabelCompany.stopwords_zh_company:
					if stopword in key:
						flag = False
						func(beginindex, key, mydict, setvalues, txt)
						break
				if flag:
					index = keywords[key][1]
					test = RegexUtils.get_word_nospecial(txt[index:index + 8]).lstrip()
					for stopword in PutLabelCompany.stopwords_zh_company_1:
						if stopword in test:
							func(beginindex, key, mydict, setvalues, txt)
							# # issim = False
							# valset = mydict[key]
							# for val in valset:
							# 	extra = val.replace(key, "")
							# 	if stopword in MatchCompany.similar_dict:
							# 		sims = MatchCompany.similar_dict[stopword]
							# 		if sims and extra in sims and test in sims:
							# 			# issim = True
							# 			# setsimilar.add("{0}{1} 【 公司相似 】".format(key, valset))
							# 			# setvalues.add("{0}{1}".format(key, valset))
							# 			setvalues[key] = list(valset)
							# 			break
							# if not issim:
							# setcompany_fuzzy.add("{0}{1}".format(key, valset))
							# setcompany_fuzzy[key] = list(valset)
							break
			else:
				indexchar = txt[beginindex - 1:beginindex]
				if not RegexUtils.contain_en(indexchar):
					index = keywords[key][1]
					indexchar = txt[index:index + 1]
					if not RegexUtils.contain_en(indexchar):
						func(beginindex, key, mydict, setvalues, txt)
	mapresult[matchtype] = setvalues


def match_drug(txt, tokenizer, mydict, mapresult, matchtype):
	setvalues = {}
	keywords = tokenizer.cutwkz_dict(txt)
	if keywords:
		if "database" in matchtype:
			for key in keywords:
				beginindex = keywords[key][0]
				match_drug_database(beginindex, key, mydict, setvalues, txt)
		else:
			for key in keywords:
				beginindex = keywords[key][0]
				match_drug_discover(beginindex, key, mydict, setvalues, txt)
	mapresult[matchtype] = setvalues


def putlabel_core(text, putlabeltype, showdetails):
	"""

	:param text:
	:param putlabeltype: 0全部,1公司,2药品,3疾病,4靶点
	:param showdetails:
	:return:
	"""
	if not text:
		return None
	text = BeautifulSoup(text, "html.parser").get_text().replace("\n", "")
	# 去括号里面东西
	txt = text.replace("（", "(").replace("）", ")")
	txt = RegexUtils.replace_diy_chars(txt, "\(.*?\)")
	txt = RegexUtils.replace_diy_chars(txt, "\[.*?\]")
	txt = " ".join(txt.split())
	txt = RegexUtils.replace_special_chars_nosplit(txt)
	txt = txt.lower()
	mapresult = {}
	# 匹配公司
	if putlabeltype == 0 or putlabeltype == 1:
		match_company(txt, tokenizer_database_company, dict_database_company, mapresult, "database_company",
					  match_company_database)
		match_company(txt, tokenizer_discover_company, dict_discover_company, mapresult, "discover_company",
					  match_company_discover)
	# 匹配药品
	if putlabeltype == 0 or putlabeltype == 2:
		match_drug(txt, tokenizer_database_drug, dict_database_drug, mapresult, "database_drug")
		match_drug(txt, tokenizer_discover_drug, dict_discover_drug, mapresult, "discover_drug")
	# 匹配疾病
	if putlabeltype == 0 or putlabeltype == 3:
		match_drug(txt, tokenizer_discover_indication, dict_discover_indication, mapresult, "discover_indication")
	# 匹配靶点
	if putlabeltype == 0 or putlabeltype == 4:
		match_drug(txt, tokenizer_discover_target, dict_discover_target, mapresult, "discover_target")
	return mapresult


# 定时更新字典
def timer_load_dict(readcache):
	print("【开始更新字典】【%s】" % time.strftime(ISOTIMEFORMAT, time.localtime()))
	initialized = False
	try:
		dict_discover_indication, jieba_dict_discover_indication = PutLabelIndication.writedict(isdiscover=True,
																								readcache=readcache)
		tokenizer_discover_indication.initialized = initialized
		tokenizer_discover_indication.initialize(jieba_dict_discover_indication)

		dict_discover_target, jieba_dict_discover_target = PutLabelTarget.writedict(isdiscover=True,
																					readcache=readcache)
		tokenizer_discover_indication.initialized = initialized
		tokenizer_discover_target.initialize(jieba_dict_discover_target)

		dict_database_drug, jieba_dict_database_drug = PutLabelDrug.writedict(isdiscover=False, readcache=readcache)
		tokenizer_database_drug.initialized = initialized
		tokenizer_database_drug.initialize(jieba_dict_database_drug)

		dict_discover_drug, jieba_dict_discover_drug = PutLabelDrug.writedict(isdiscover=True, readcache=readcache)
		tokenizer_discover_drug.initialized = initialized
		tokenizer_discover_drug.initialize(jieba_dict_discover_drug)

		dict_database_company, jieba_dict_database_company = PutLabelCompany.writedict(isdiscover=False,
																					   readcache=readcache)
		tokenizer_database_company.initialized = initialized
		tokenizer_database_company.initialize(jieba_dict_database_company)

		dict_discover_company, jieba_dict_discover_company = PutLabelCompany.writedict(isdiscover=True,
																					   readcache=readcache)
		tokenizer_discover_company.initialized = initialized
		tokenizer_discover_company.initialize(jieba_dict_discover_company)
	except Exception as e:
		print("【更新字典失败】【%s】：%s" % (time.strftime(ISOTIMEFORMAT, time.localtime()), e))


# 重新加载字典
def reload_dict(readcache):
	# 定时更新字典(凌晨1点)
	# scheduler = BlockingScheduler()	# 阻塞
	scheduler = BackgroundScheduler()  # 非阻塞
	# scheduler.add_job(func=timer_load_dict, trigger="cron", args=(readcache,), year="*", month="*", day="*", hour="*",
	# 				  minute="*", second=58, id="MatchTotal")
	scheduler.add_job(func=timer_load_dict, trigger="cron", args=(readcache,), year="*", month="*", day="*", hour=1,
					  id="MatchTotal")
	scheduler.start()


# 读取字典
def read_dict(readcache):
	global dict_discover_indication, dict_discover_target, dict_database_drug, dict_discover_drug, dict_database_company, dict_discover_company, tokenizer_discover_indication, tokenizer_discover_target, tokenizer_database_drug, tokenizer_discover_drug, tokenizer_database_company, tokenizer_discover_company
	dict_discover_indication, jieba_dict_discover_indication = PutLabelIndication.writedict(isdiscover=True,
																							readcache=readcache)
	dict_discover_target, jieba_dict_discover_target = PutLabelTarget.writedict(isdiscover=True, readcache=readcache)
	dict_database_drug, jieba_dict_database_drug = PutLabelDrug.writedict(isdiscover=False, readcache=readcache)
	dict_discover_drug, jieba_dict_discover_drug = PutLabelDrug.writedict(isdiscover=True, readcache=readcache)
	dict_database_company, jieba_dict_database_company = PutLabelCompany.writedict(isdiscover=False,
																				   readcache=readcache)
	dict_discover_company, jieba_dict_discover_company = PutLabelCompany.writedict(isdiscover=True, readcache=readcache)
	# 初始化分词器
	tokenizer_discover_indication = jieba.Tokenizer(jieba_dict_discover_indication)
	tokenizer_discover_target = jieba.Tokenizer(jieba_dict_discover_target)
	tokenizer_database_drug = jieba.Tokenizer(jieba_dict_database_drug)
	tokenizer_discover_drug = jieba.Tokenizer(jieba_dict_discover_drug)
	tokenizer_database_company = jieba.Tokenizer(jieba_dict_database_company)
	tokenizer_discover_company = jieba.Tokenizer(jieba_dict_discover_company)

	# match_from_mongodb()
	# match_from_mysql()
	# text = "除复星医药外，北京万生药业有限责任公司、南京正大天晴制药有限公司已获雷迪帕韦索氟布韦片的临床批件inC.。"
	# print(putlabel_core(text, 1, None))
	# 本机只能通过127.0.0.1或者localhost可访问,其它机子只能通过192.168.2.135可以访问(默认是5000)
	app.run(host='0.0.0.0', port=5001, debug=True)


if __name__ == '__main__':
	# 字典是否从缓存中读取
	readcache = False

	reload_dict(readcache)
	read_dict(readcache)

	print("\nover")
