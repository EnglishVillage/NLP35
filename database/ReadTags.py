#!/usr/bin/python
# -*- coding:utf-8 -*-
import os, sys
from functools import cmp_to_key
import jieba
import jieba.posseg as pseg
import time
from operator import itemgetter, attrgetter
import re
from flask import Flask, jsonify, abort, make_response, request
from bs4 import BeautifulSoup

# 导入自定义的包
sys.path.append(os.path.join("..", "utils"))
from utils import OtherUtils, MysqlUtils

app = Flask(__name__)


def addtag(set: set, value):
	"""
	将值转化为str并添加到set集合中
	:param set: set集合
	:param value: 值
	:return: 空
	"""
	if value is not None:
		if type(value) is str:
			value = value.strip()
			if value:
				value = value.lower().replace("\n", "")
				set.add(value)
		else:
			set.add(str(value).strip())


def rowstoset(rows: tuple):
	myset = set()
	for row in rows:
		if isinstance(row, tuple):
			for value in row:
				addtag(myset, value)
		else:
			addtag(myset, row)
	return myset


def sqltoset(sql: str):
	rows = MysqlUtils.getrows(sql)
	return rowstoset(rows)


# 从mysql获取到关键字存储到文件中的路径
createdict_all = os.path.join("..", "sources", "createdict_all")
createdict_target = os.path.join("..", "sources", "createdict_target")
createdict_company = os.path.join("..", "sources", "createdict_company")
createdict_indication = os.path.join("..", "sources", "createdict_indication")
createdict_drug = os.path.join("..", "sources", "createdict_drug")
# 自定义分词器
tokenizer_all = None
tokenizer_target = None
tokenizer_company = None
tokenizer_indication = None
tokenizer_drug = None
# 关键字集合
set_all = None
set_target = None
set_company = None
set_indication = None
set_drug = None

# 自定义的词库的词频和类型
freqandtag = "@@3@@nz"


def writefile(path: str, set: set):
	# 写入到文件中
	with open(path, "w", encoding="utf8") as f:
		tagList = list(set)
		tagList.sort(key=lambda str: len(str), reverse=False)
		length = len(tagList) - 1
		# 这里只遍历N-1个元素,因为每页有加换行符
		for i in range(length):
			# 如果长度小于2的词语则不添加到词库中
			if len(tagList[i]) < 2:
				continue
			else:
				for i in range(i, length):
					f.write(tagList[i] + freqandtag + "\n")
				break
		# 最後一个没有换行符
		f.write(tagList[length] + freqandtag)


def writetags():
	global set_target
	global set_company
	global set_indication
	global set_drug
	global set_all
	set_target = sqltoset(
		"select abbreviation,standard_name,name_cn,full_name,alternative_name from yymf_discover_target")
	set_company = sqltoset(
		"select standard_name_en,standard_name_cn,full_name_en,full_name_cn,alternative_name,name_FDA from yymf_discover_company")
	set_indication = sqltoset("select standard_name_cn,standard_name_en,alternative_name from yymf_discover_indication")
	set_drug = sqltoset(
		"select standard_name,simplified_standard_name,bridging_name,active_ingredient_cn,active_ingredient_en,alternative_active_ingredient_name,inn_cn,inn_en,alternative_inn,trade_name_en,trade_name_cn,generic_brand,investigational_code,declaration_cn from yymf_discover_drugs_name_dic")
	# 合集
	# set_all=set_target.union(set_company).union(set_indication).union(set_drug)
	set_all = set_target | set_company | set_indication | set_drug

	writefile(createdict_target, set_target)
	writefile(createdict_company, set_company)
	writefile(createdict_indication, set_indication)
	writefile(createdict_drug, set_drug)
	writefile(createdict_drug, set_all)


def jiebaanalyse(tokenizer, text, wordsset):
	"""
	使用jieba分词之后再进行获取关键字
	:param keywordsset:
	:param text:
	:return:
	"""

	keywordsset = set()

	# 这里cut_all要设置为False,设置为True,则会出现多余重复的分词
	lcut = tokenizer.lcut(text.lower(), cut_all=False, HMM=False)
	length = len(lcut)
	for i in range(length):
		str = lcut[i]
		# 只获取分词後长度大于1的词组
		if len(str) > 1:
			# 从第2个字符串开始
			if i > 0:
				# 尾字符是字母或者数字,判断后一个是否为字母或者数字
				if i < length - 1 and OtherUtils.contain_eng(str[-1]):
					if not OtherUtils.contain_eng(lcut[i + 1][0]):
						# 首字符是字母或者数字,判断前一个是否为字母或者数字
						if OtherUtils.contain_eng(str[0]):
							if not OtherUtils.contain_eng(lcut[i - 1][-1]):
								# 判断是否包含在词库中
								if str in wordsset:
									keywordsset.add(str)
						else:
							# 判断是否包含在词库中
							if str in wordsset:
								keywordsset.add(str)
				# 首字符是字母或者数字,判断前一个是否为字母或者数字
				elif OtherUtils.contain_eng(str[0]):
					if not OtherUtils.contain_eng(lcut[i - 1][-1]):
						# 判断是否包含在词库中
						if str in wordsset:
							keywordsset.add(str)
				else:
					# 判断是否包含在词库中
					if str in wordsset:
						keywordsset.add(str)
			# 尾字符是字母或者数字,判断后一个是否为字母或者数字
			elif OtherUtils.contain_eng(str[-1]):
				if not OtherUtils.contain_eng(lcut[i + 1][0]):
					# 判断是否包含在词库中
					if str in wordsset:
						keywordsset.add(str)
			else:
				# 判断是否包含在词库中
				if str in wordsset:
					keywordsset.add(str)
	return keywordsset


def diyanalyse(tokenizer, text):
	"""
	使用自定义获取关键字
	:param text:
	:return:
	"""
	return tokenizer.lcutwkz(text)


# 400页面
@app.errorhandler(400)
def not_found(error):
	return make_response(jsonify({'error': '没有接收到可用数据!(No data was received!)'}), 404)


@app.route("/")
def index():
	return "Hello, World!"


def keywords(tokenizer: jieba.Tokenizer):
	# 使用Body中的x-www.form.urlencoded进行发送
	if len(request.values) < 1:
		abort(400)

	text = request.values["text"]
	# text = (
	# 	"李小福果糖-1,6-二磷酸酶是 dalian holley kingkong pharmaceutical co., ltd.创新办主任G蛋白偶联受体49也是补体因子H和云计算方面的专家; 什么是prostate stem cell antigen (psca)或者八一双鹿\n"
	# 	"例如我解旋酶-引物酶输入G蛋白偶联受体49一个带“韩玉赏鉴”的标题，Edu Trust认证在补体受体2自定义词库中成纤维细胞生长因子18也增加了此词为N类\n"
	# 	"「台中」正確钠离子通道Nav1.8應該不會wang kun zao被切開α5β1整合素。mac上可分出「石墨烯」；此時又可以分出來二磷酸尿核苷葡糖醛酸基转移酶1家族肽A1凱特琳了。\n"
	# 	"怎样Citroën growth可以强制insulin-like growth factor 1 receptor hi提高一些关键词中一些词果糖-1,6-二磷酸酶的权重呀血管紧张素(1-7)")
	# text = "李小福果糖-1,6-二磷酸酶是 dalian holley kingkong pharmaceutical co., ltd.创新pdkg办主任apdk G蛋白偶联受体49也是补体因子H和云计算pdk方面的pdkz专家; 什么是prostate stem cell antigen (psca)或者八一双鹿"

	if text:
		# 去html并转小写
		text = BeautifulSoup(text, "html.parser").get_text()
		# print(text)
		# 1.使用jieba分词之后再进行获取关键字
		# keywordsset = jiebaanalyse(tokenizer, text, set_all)
		# # 2.使用自定义获取关键字
		keywordsset = diyanalyse(tokenizer, text)

		# for x in keywordsset:
		# 	print(x)

		# 返回json串
		return jsonify({'keywords': list(keywordsset)}), 200
	else:
		# 返回json串
		return jsonify({'keywords': None}), 200


# post请求
@app.route('/python/api/keywords/all', methods=['POST'])
def keywordsall():
	return keywords(tokenizer_all)


# post请求
@app.route('/python/api/keywords/target', methods=['POST'])
def keywordstarget():
	return keywords(tokenizer_target)


# post请求
@app.route('/python/api/keywords/company', methods=['POST'])
def keywordscompany():
	return keywords(tokenizer_company)


# post请求
@app.route('/python/api/keywords/indication', methods=['POST'])
def keywordsindication():
	return keywords(tokenizer_indication)


# post请求
@app.route('/python/api/keywords/drug', methods=['POST'])
def keywordsdrug():
	return keywords(tokenizer_drug)


if __name__ == '__main__':
	# 从数据库读取关键字并存储到文件中
	writetags()

	# 自定义分词器
	# /tmp/jieba.u7eb91ea902d04d0df9cb8780d09ea208.cache
	tokenizer_all = jieba.Tokenizer(createdict_all)
	tokenizer_target = jieba.Tokenizer(createdict_target)
	tokenizer_company = jieba.Tokenizer(createdict_company)
	tokenizer_indication = jieba.Tokenizer(createdict_indication)
	tokenizer_drug = jieba.Tokenizer(createdict_drug)

	# 本机只能通过127.0.0.1或者localhost可访问,其它机子只能通过192.168.2.135可以访问(默认是5000)
	app.run(host='0.0.0.0', port=5000, debug=True)
# keywords()
