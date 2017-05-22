#!/usr/bin/python
# -*- coding:utf-8 -*-

import os, sys, re, time
from collections import OrderedDict
from operator import itemgetter
import pypinyin
import Levenshtein
from flask import Flask, jsonify, abort, make_response, request
from utils import OtherUtils, MysqlUtils, MongodbUtils, IOUtils, CollectionUtils

app = Flask(__name__)
dict_dict = None


def preDeal(key: str, value, mydict):
	# 去掉(XXXX)和[XXX]
	key = re.sub(r"\(.*?\)", "", key)
	key = re.sub(r"\[.*?\]", "", key)
	if "重组人乳头瘤病毒" in key:
		split = [key]
	else:
		split = re.split(';|/', key)
		if len(split) > 5:
			split = [key]
	for s in split:
		# 去前後空格,去特殊字符
		s = re.sub(OtherUtils.special_chars, "", s.lstrip())
		if len(s) > 1:
			s = " ".join(s.split())
			# 添加字典里的值作为key
			CollectionUtils.add_dict_setvalue_multi(mydict, s, value)
			# 将值转化为全拼音作为key
			newstr = pypinyin.slug(s, separator="")
			CollectionUtils.add_dict_setvalue_multi(mydict, newstr, value)
			# 将值的首字母作为key
			newstr = pypinyin.slug(s, separator="", style=pypinyin.FIRST_LETTER)
			CollectionUtils.add_dict_setvalue_multi(mydict, newstr, value)


def writedict():
	path = OtherUtils.get_target_path("searchdrugdict.txt")
	global dict_dict
	dict_dict = {}
	isexist = os.path.exists(OtherUtils.get_target_path("searchdrugdict.txt"))
	if isexist:
		with open(path, "r", encoding="utf-8") as f:
			for line in f.readlines():
				if line:
					line = line.lstrip("('").rstrip("'})\n")
					ls = line.split("', {'")
					try:
						dict_dict[ls[0]] = set(ls[1].split("', '"))
					except:
						ls = line.lstrip("('").rstrip("\"})\n").split("', {\"")
						dict_dict[ls[0]] = set(ls[1].split("\", \""))
	else:
		mydict = MysqlUtils.sql_to_dict(
			"select standard_name,standard_name,simplified_standard_name,inn_cn,inn_en,trade_name_en,trade_name_cn,investigational_code,declaration_cn "
			"from yymf_discover_drugs_name_dic")
		for s in mydict:
			preDeal(s, mydict[s], dict_dict)
		mylist = list(dict_dict.items())
		mylist.sort(key=lambda t: len(t[0]), reverse=True)
		# mylist = list(dict_dict.keys())
		# mylist.sort(key=lambda t: len(t), reverse=True)
		IOUtils.my_write(path, mylist)


# 400页面
@app.errorhandler(400)
def not_found(error):
	return make_response(jsonify({'error': '没有接收到可用数据!(No data was received!)'}), 404)


@app.route("/")
def index():
	return "Hello, World!"


@app.route('/python/api/search/drug', methods=['POST'])
def search():
	# 使用Body中的x-www.form.urlencoded进行发送
	if len(request.values) < 1:
		abort(400)
	text = request.values["text"]
	result = search_debug(text)
	return jsonify({'match': result}), 200


def split_tuple(ls, result, size=-1):
	if size>-1:
		i = 0
		flag = False
		for t in ls:
			if len(t[0]) > 1:
				for v in t[0]:
					if not v in result:
						result[v] = (v, t[1], t[2], t[3])
						i += 1
						if i >= size:
							flag = True
							break;
			elif not t[0][0] in result:
				result[t[0][0]] = (t[0][0], t[1], t[2], t[3])
				i += 1
				if i >= size:
					flag = True
					break;
			if flag:
				break
	else:
		for t in ls:
			if len(t[0]) > 1:
				for v in t[0]:
					if not v in result:
						result[v] = (v, t[1], t[2], t[3])
			elif not t[0][0] in result:
				result[t[0][0]] = (t[0][0], t[1], t[2], t[3])
	return result


def get_most(values, winkler):
	mostdict = OrderedDict()
	nomostdict = OrderedDict()
	first = sorted(values[0][0], key=lambda v: len(v))
	for f in first:
		mostdict[f] = (f, values[0][1], values[0][2], values[0][3])
	if len(first) > 1:
		for value in values:
			if value[1] <= winkler:
				for v in value[0]:
					flag = False
					for s in first:
						if s in v:
							if not v in mostdict:
								mostdict[v] = (v, value[1], value[2], value[3])
							flag = True
							break
					if not flag and not v in nomostdict:
						nomostdict[v] = (v, value[1], value[2], value[3])
			else:
				break
	else:
		for value in values:
			if value[1] <= winkler:
				for v in value[0]:
					if first[0] in v:
						if not v in mostdict:
							mostdict[v] = (v, value[1], value[2], value[3])
						break
					elif not v in nomostdict:
						nomostdict[v] = (v, value[1], value[2], value[3])
			else:
				break
	return [list(mostdict.values()), list(nomostdict.values())]


# 匹配的条数
show_num = 5
# 中文模糊拼音
fuzzy_dict = {"c": "ch", "s": "sh", "z": "zh", "l": "n", "f": "h", "r": "l", "an": "ang", "en": "eng", "in": "ing", "ian": "iang", "uan": "uang", "ch": "c", "sh": "s", "zh": "z", "n": "l", "h": "f", "l": "r", "ang": "an", "eng": "en", "ing": "in", "iang": "ian", "uang": "uan"}
fuzzy_set = {"c", "s", "z", "f", "l", "r", "an", "en", "in", "ian", "uan"}


def search_core(text):
	text = text.rstrip("\n").lstrip()
	matchdict = {}
	is_fuzzy = False
	for fuzzy in fuzzy_set:
		if fuzzy in fuzzy_set:
			is_fuzzy = True
			break
	# 相似度计算
	if is_fuzzy:
		for key in dict_dict:
			# 本来是越大越好,转化为越小越好
			winkler = 1 - Levenshtein.jaro_winkler(text, key, 0.12)
			distance = Levenshtein.distance(text, key)
			# ratio = Levenshtein.ratio(text, key)
			# if (winkler > 0.8 or ratio > 0.4) and distance < 20:
			ratio = 0
			if winkler < 0.3:
				value = tuple(dict_dict[key])
				if value in matchdict:
					t = matchdict[value]
					if winkler < t[1]:
						matchdict[value] = (value, winkler, distance, ratio)
				else:
					matchdict[value] = (value, winkler, distance, ratio)
	else:
		for key in dict_dict:
			# 本来是越大越好,转化为越小越好
			winkler = 1 - Levenshtein.jaro_winkler(text, key, 0.12)
			distance = 0
			ratio = 0
			if winkler < 0.3:
				value = tuple(dict_dict[key])
				if value in matchdict:
					t = matchdict[value]
					if winkler < t[1]:
						matchdict[value] = (value, winkler, distance, ratio)
				else:
					matchdict[value] = (value, winkler, distance, ratio)
	if matchdict:
		values = matchdict.values()
		if is_fuzzy:
			similar_list = filter(lambda t: t[2] < 3, values)
			similar_list = sorted(similar_list, key=itemgetter(2, 1))
			similar_list = split_tuple(similar_list, OrderedDict(), show_num)
			similar_list=[r for r in similar_list.values()]
			print(similar_list)
			values = sorted(values, key=itemgetter(1, 2))
		else:
			similar_list = None
			values = sorted(values, key=itemgetter(1))
		# 精确匹配(判断jaro_winkler算法是否完全匹配)
		if values[0][1] <= 0.0:
			arr = get_most(values, 0.2)
			return arr[0][:show_num], arr[1][:show_num], similar_list
		# 模糊匹配
		result = split_tuple(values, OrderedDict(), show_num)
		return None, [r for r in result.values()], similar_list
	return None, None, None

def search_debug(text):
	match, nomatch, similar = search_core(text)
	if match:
		if nomatch:
			match.extend(nomatch)
		if similar:
			matchset=set(match)
			i=0
			for t in similar:
				if not t in match:
					match.append(t)
					matchset.add(t)
					i+=1
					if i>=show_num:
						break;
		return match
	elif nomatch:
		if similar:
			matchset = set(nomatch)
			i = 0
			for t in similar:
				if not t in nomatch:
					nomatch.append(t)
					matchset.add(t)
					i += 1
					if i >= show_num:
						break;
		return nomatch
	else:
		return similar


if __name__ == '__main__':
	writedict()
	# 本机只能通过127.0.0.1或者localhost可访问,其它机子只能通过192.168.2.135可以访问(默认是5000)
	# app.run(host='0.0.0.0', port=5000, debug=True)
	# amxl amlz
	print(search_debug("slxl"))
