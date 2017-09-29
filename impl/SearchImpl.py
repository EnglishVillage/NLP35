#!/usr/bin/python3.5
# -*- coding:utf-8 -*-

"""
	搜索提示
"""

import os, sys, re, time

sys.path.append('/home/esuser/NLP35')
from collections import OrderedDict
from operator import itemgetter

import jieba
import pypinyin
import Levenshtein
from bs4 import BeautifulSoup
from flask import Flask, jsonify, abort, make_response, request

from utils import OtherUtils, IOUtils, CollectionUtils, RegexUtils, JiebaUtils
from utils.Utils import MysqlUtils, MongodbUtils


app = Flask(__name__)
mysql_utils = MysqlUtils()
mongodb_utils = MongodbUtils("cfda_news_notify_content")

dict_dict = {}
dict_zh = {}
dict_en = {}
# 常用模糊字典
dict_default_fuzzy = {}
exclude_set = set()

# jaro_winkler算法的前缀权重
bound = 0.14
# 匹配的条数
show_num = 5
# 中文模糊拼音
py_fuzzy_dict = {"c": "ch", "s": "sh", "z": "zh", "l": "n", "f": "h", "r": "l", "an": "ang", "en": "eng", "in": "ing", "ian": "iang", "uan": "uang", "ch": "c", "sh": "s", "zh": "z", "n": "l", "h": "f", "l": "r", "ang": "an", "eng": "en", "ing": "in", "iang": "ian", "uang": "uan"}
py_fuzzy_set = {"c", "s", "z", "f", "l", "r", "an", "en", "in", "ian", "uan"}
sql_discover_drugs = "select standard_name,standard_name,simplified_standard_name,inn_en,trade_name_en,investigational_code,declaration_cn from yymf_discover_drugs_name_dic "
sql_database_drugs = "select standard_name,alternative_inn,alternative_active_ingredient_name,alternative_name from yymf_drugs_name_dic where is_delete!=1 "

# sql = "select standard_name,alternative_inn,alternative_active_ingredient_name,alternative_name from yymf_drugs_name_dic "
# sql_discover_drugs += "where standard_name in ('中/长链脂肪乳C6-24')"
# sql_discover_drugs += "where standard_name like '%阿莫西林%'"
# sql_database_drugs+="where standard_name in ('卫生散')"
# sql_database_drugs += "where standard_name like '%消渴平%'"
jieba_dict_path = None


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
	showdetails = False
	if "showdetails" in request.values:
		showdetails = True
	result = search_debug_details(text, showdetails)
	return jsonify({'match': result}), 200


def preDeal(mydict, isfuzzymatch=True, isdiscover=True):
	activedict = {}
	# 遍历出来的key是用来做为value
	for value in mydict:
		keys = mydict[value]
		for key in keys:
			key = key.replace("（", "(").replace("）", ")")
			key = re.sub(r"\(.*?\)", "", key)
			key = re.sub(r"\[.*?\]", "", key)
			keysplit = re.split(';|\|', key)
			for keychi in keysplit:
				# 以+和/分割的是活性成分
				if isdiscover:
					keychisplit = keychi.split("/")
				else:
					keychisplit = keychi.split("+")
				if len(keychisplit) > 1:
					isactive = True
				else:
					isactive = False
				for keychichi in keychisplit:
					# 去前後空格,去特殊字符
					keychichi = keychichi.strip()
					keychichi = re.sub(RegexUtils.special_chars, "", keychichi)
					if keychichi:
						keychichi = " ".join(keychichi.split())
						# 模糊匹配则添加首字母作为key
						if isfuzzymatch:
							if not isactive:
								# 将值的拼音首字母作为key
								newstr = pypinyin.slug(keychichi, separator="", style=pypinyin.FIRST_LETTER)
								if len(newstr) < 11:
									CollectionUtils.add_dict_setvalue_single(dict_dict, newstr, value)
								# 将值转化为全拼音作为key
								newstr = pypinyin.slug(keychichi, separator="")
								if len(newstr) < 20:
									CollectionUtils.add_dict_setvalue_single(dict_dict, newstr, value)
						# 精确匹配,则去除一些有歧义的词,防止过拟合
						else:
							flag = False
							for exclude in exclude_set:
								if keychichi in exclude:
									flag = True
							if flag:
								continue
						# 添加字典里的值作为key
						if isactive:
							CollectionUtils.add_dict_setvalue_single(activedict, keychichi, value)
						else:
							CollectionUtils.add_dict_setvalue_single(dict_dict, keychichi, value)
	# 对活性成份列表进行判断
	for key in activedict:
		# 判断活性成份作为key是否已经存在
		if key in dict_dict:
			CollectionUtils.add_dict_setvalue_multi(dict_dict, key, activedict[key])
		else:
			# 判断活性成份是否为value的一部分
			vals = activedict[key]
			for val in vals:
				if key in val.lower():
					CollectionUtils.add_dict_setvalue_multi(dict_dict, key, activedict[key])
					break
	print("pre deal over!")


def split_dict(isfuzzymatch):
	new_dict = {}
	for key in dict_dict:
		keylen = len(key)
		# 判断是否全部数字或者长度大于30
		if key.isdigit() or keylen > 30:
			continue
		elif RegexUtils.contain_zh(key):
			if keylen < 21 and keylen > 1:
				valueset = dict_dict[key]
				if isfuzzymatch:
					dict_zh[key] = valueset
					new_dict[key] = valueset
				else:
					if keylen < 3:
						for value in valueset:
							if key == value:
								dict_zh[key] = valueset
								new_dict[key] = valueset
					else:
						dict_zh[key] = valueset
						new_dict[key] = valueset
					# valueset = dict_dict[key]
					# dict_zh[key] = valueset
					# new_dict[key] = valueset
		elif keylen > 1:
			dict_en[key] = dict_dict[key]
			new_dict[key] = dict_dict[key]
	return new_dict


def remove_multi_drug(zhlist):
	newlist = []
	# mulset用来记录最短的key
	mulset = set()
	for t in zhlist:
		flag = True
		for key in mulset:
			if key in t[0]:
				flag = False
				break
		if flag:
			mulset.add(t[0])
			newlist.append(t)
	return newlist


def writedict(isfuzzymatch=True, isdiscover=True, readcache=False, returntype=0):
	"""

	:param isfuzzymatch:
	:param isdiscover:
	:param readcache:
	:param returntype:0:中英文,1:中文,2:英文
	:return:
	"""
	# 获取字典缓存路径名和结巴字典缓存路径名
	tempfile = ""
	filename = "dict_drug"
	jieba_filename = "jieba_drug"
	if isfuzzymatch:
		tempfile += "_fuzzy"
	else:
		tempfile += "_exact"
	if isdiscover:
		tempfile += "_discover"
	else:
		tempfile += "_database"
	path_zh = IOUtils.get_path_target(filename + tempfile + "_zh.txt")
	path_en = IOUtils.get_path_target(filename + tempfile + "_en.txt")
	global jieba_dict_path
	jieba_dict_path = IOUtils.get_path_target(jieba_filename + tempfile + ".txt")
	# 判断缓存文件是否存在
	isexist = os.path.exists(path_zh)
	if readcache and isexist:
		IOUtils.my_read_tuple_set(path_zh, dict_zh)
		IOUtils.my_read_tuple_set(path_en, dict_en)
		if returntype == 0:
			new_dict = dict(dict_zh, **dict_en)
			return new_dict
		elif returntype == 1:
			return dict_zh
		elif returntype == 2:
			return dict_en
	else:
		# 精确匹配,则加载排除字典
		if not isfuzzymatch:
			IOUtils.load_exclude(("chinacity.txt", "exclude_drug.txt"), exclude_set)
		if isdiscover:
			mydict = mysql_utils.sql_to_dict(sql_discover_drugs)
		else:
			mydict = mysql_utils.sql_to_dict(sql_database_drugs)
		preDeal(mydict, isfuzzymatch, isdiscover)
		new_dict = split_dict(isfuzzymatch)

		zhlist = list(dict_zh.items())
		enlist = list(dict_en.items())

		# 模糊匹配,去除多余的key
		if isfuzzymatch:
			# 这里先升序
			zhlist.sort(key=lambda t: len(t[0]), reverse=False)
			zhlist = remove_multi_drug(zhlist)
			# 重新赋值
			global dict_zh
			dict_zh = dict(zhlist)
			new_dict = dict(dict_zh, **dict_en)

		zhlist.sort(key=lambda t: len(t[0]), reverse=True)
		IOUtils.my_write(path_zh, zhlist)
		enlist.sort(key=lambda t: len(t[0]), reverse=True)
		IOUtils.my_write(path_en, enlist)

		dict_set = set(new_dict.keys())
		JiebaUtils.writefile(jieba_dict_path, dict_set)

		# mylist = list(dict_zh.keys())
		# mylist.sort(key=lambda t:len(t),reverse=True)
		# IOUtils.my_write(path_zh, mylist)
		if returntype == 0:
			return new_dict
		elif returntype == 1:
			return dict_zh
		elif returntype == 2:
			return dict_en


def loadfuzzydict():
	fuzzys = IOUtils.my_read_source("searchdrugfuzzy.txt", [])
	for s in fuzzys:
		key = pypinyin.slug(s, separator="")
		CollectionUtils.add_dict_setvalue_single(dict_default_fuzzy, key, s)
		key = pypinyin.slug(s, separator="", style=pypinyin.FIRST_LETTER)
		CollectionUtils.add_dict_setvalue_single(dict_default_fuzzy, key, s)


def get_matchdict(text, dict_temp, matchdict, func):
	"""
	计算相似度
	:param text: 用户输入字符串
	:param dict_temp: 字典
	:param matchdict: 存储相似度的dict集合
	:param func: 计算distance的方法
	:return: None
	"""
	for key in dict_temp:
		# 判断是否相等
		if text == key:
			matchdict.clear()
			value = tuple(dict_temp[key])
			matchdict[value] = (value, 0, 0, 0)
			break
		# 本来是越大越好,转化为越小越好
		winkler = 1 - Levenshtein.jaro_winkler(text, key, bound)
		winkler_temp = 1 - Levenshtein.jaro_winkler(text[::-1], key[::-1], bound)
		if winkler_temp < winkler:
			winkler = winkler_temp
		distance = func(text, key)
		ratio = 0
		# ratio = Levenshtein.ratio(text, key)
		# if (winkler > 0.8 or ratio > 0.4) and distance < 20:
		if winkler < 0.3:
			# 获取匹配到的关键字
			value = tuple(dict_temp[key])
			if value in matchdict:
				if winkler < matchdict[value][1]:
					matchdict[value] = (value, winkler, distance, ratio)
			else:
				matchdict[value] = (value, winkler, distance, ratio)


def get_exact_match(values, winkler):
	"""
	获取精确匹配的列表
	:param values:所有列表
	:param winkler: 相似度阈值
	:return:精确匹配的列表
	"""
	mostdict = OrderedDict()
	first = sorted(values[0][0], key=lambda v: len(v))
	for f in first:
		mostdict[f] = (f, values[0][1], values[0][2], values[0][3])
	if len(first) > 1:
		for value in values:
			if value[1] <= winkler:
				for v in value[0]:
					for s in first:
						if s in v:
							if not v in mostdict:
								mostdict[v] = (v, value[1], value[2], value[3], len(v))
							break
			else:
				break
	else:
		exact = first[0]
		for value in values:
			if value[1] <= winkler:
				for v in value[0]:
					if exact in v:
						if not v in mostdict:
							mostdict[v] = (v, value[1], value[2], value[3], len(v))
						break
			else:
				break
	return list(mostdict.keys())


def split_tuple(ls, text, is_py_fuzzy, size=0, *items):
	"""
	对ls里面多个拆分成单个
	:param ls: 要拆分的集合列表[(set(), winkler, distance, ratio)]
	:param size: 截取个数
	:param items: 排序方式
	:return: list
	"""
	if not ls:
		return None
	result = OrderedDict()
	if size > 0:
		text_py = pypinyin.slug(text, separator="")  # 得到拼音
		firstindex = items[0]
		# 获取最低的相似度
		if len(ls) > size:
			crucial = ls[size - 1][1]
		else:
			crucial = ls[-1][1]
		for t in ls:
			if t[1] > crucial:
				break;
			if len(t[0]) > 1:
				# 这里要将t转化为list,否则下面无法对tuple赋值操作
				newtuple = ["", t[1], t[2], t[3]]
				for v in t[0]:
					if not v in result:
						# 这里进行文本相似度判断(包含关系)
						lower = v.lower()
						textlen = len(v)
						# 判断是否完全相等
						if lower == text:
							newtuple[firstindex] = 0
						else:
							lenscore = 0.5 / textlen
							newtuple[firstindex] = t[firstindex]
							# 判断是否有包含关系
							if text in lower:
								newtuple[3] = 0.25
							elif lower in text:
								newtuple[3] = 0.5 + lenscore
							else:
								# 含有中文,则判断拼音的包含关系
								if not is_py_fuzzy:
									keypy = pypinyin.slug(lower, separator="")
									if text_py == keypy:
										newtuple[3] = 0.05
									elif text_py in keypy:
										newtuple[3] = 0.30
									elif keypy in text_py:  # 判断字典里的拼音是否被搜索词包含:
										newtuple[3] = 0.55 + lenscore
									else:
										newtuple[3] = 1
								else:
									newtuple[3] = 1
						result[v] = (v, newtuple[1], newtuple[2], newtuple[3], textlen)
			elif not t[0][0] in result:
				result[t[0][0]] = (t[0][0], t[1], t[2], t[3], len(t[0][0]))
		# 重新设置排序方式,添加自定义相似度的排序
		indexls = []
		indexls.append(firstindex)
		indexls.append(3)
		indexls.extend(items[1:])
		result = sorted(result.values(), key=itemgetter(*indexls))[:size]
	# else:
	# 	for t in ls:
	# 		if len(t[0]) > 1:
	# 			for v in t[0]:
	# 				if not v in result:
	# 					result[v] = (v, t[1], t[2], t[3], len(v))
	# 		elif not t[0][0] in result:
	# 			result[t[0][0]] = (t[0][0], t[1], t[2], t[3], len(t[0][0]))
	# 	result = sorted(result.values(), key=itemgetter(*items))
	return result


def search_core(text):
	# 是否有包含中文模糊拼音
	is_py_fuzzy = False
	# 判断是否包含中文
	if RegexUtils.contain_zh(text):
		dict_temp = dict_zh
	else:
		dict_temp = dict_en
		# 如果都是英文的则判断是否包含中文模糊拼音
		for fuzzy in py_fuzzy_set:
			if fuzzy in text:
				is_py_fuzzy = True
				break
	matchdict = {}
	# 相似度计算(有包含中文模糊拼音)
	if is_py_fuzzy:
		# 要求distance值
		get_matchdict(text, dict_temp, matchdict, Levenshtein.distance)
	# 相似度计算(没有包含中文模糊拼音)
	else:
		# distance设置为0
		get_matchdict(text, dict_temp, matchdict, lambda x, y: 0)
	if matchdict:
		similar_list = None
		values = matchdict.values()
		# 有包含中文模糊拼音
		if is_py_fuzzy:
			values = sorted(values, key=itemgetter(1, 2))
		else:
			values = sorted(values, key=itemgetter(1))
		# 精确匹配(判断jaro_winkler算法是否完全匹配)
		if values[0][1] <= 0.0:
			exact = get_exact_match(values, 0.2)
			return exact, None, None
		else:
			# 有包含中文模糊拼音
			if is_py_fuzzy:
				# 获得distance<3的values
				similar_list = filter(lambda t: t[2] < 3, values)
				# 根据distance和相似度从小到大排序
				similar_list = sorted(similar_list, key=itemgetter(2, 1))
				# 根据distance,相似度,匹配到的关键字的长度从小到大排序
				similar_list = split_tuple(similar_list, text, is_py_fuzzy, 2 * show_num, 2, 1, 4)
				print("similar_list:%s" % similar_list)
				# 根据相似度,distance,匹配到的关键字的长度从小到大排序
				result = split_tuple(values, text, is_py_fuzzy, show_num, 1, 2, 4)
			else:
				# 根据相似度,匹配到的关键字的长度从小到大排序
				result = split_tuple(values, text, is_py_fuzzy, show_num, 1, 4)
			return None, result, similar_list
	return None, None, None


def search_debug_details(text, isdetail=True):
	"""
	输出的模糊匹配和中文拼音模糊列表【不含有相似度】
	:param text:
	:return:
	"""
	if text:
		# 去换行符,去空格,去[]()里面的字符串,并转化为小写
		text = text.rstrip("\n").strip()
		text = re.sub(r"\[.*?\]", "", re.sub(r"\(.*?\)", "", text)).lower()
		if text:
			if " " in text or "+" in text or "/" in text:
				newtext = re.split(' |\+|\/', text)
			else:
				if text in dict_default_fuzzy:
					newtext = dict_default_fuzzy[text]
					if len(newtext) == 1:
						newtext = newtext.pop()
				else:
					newtext = text
			totalmatch, totalnomatch, totalsimilar = [], [], []
			# 根据用户输入词模糊匹配到多个
			if isinstance(newtext, set) or isinstance(newtext, list):
				j, k = 0, 0
				for chitext in newtext:
					match, nomatch, similar = search_core(chitext)
					# 针对复方
					if match:
						matchno = []
						scoreset = set()
						for drugs in match:
							i = 0
							drugsplit = re.split(' |\+|\/', drugs)
							for drug in drugsplit:
								for ctext in newtext:
									if ctext == drug:
										i += 1
									elif ctext in drug:
										i += 0.5
									elif drug in ctext:
										i += 0.75
							if i == 0:
								i = 2
							else:
								i = 1 / i
							scoreset.add(i)
							matchno.append((drugs, i, len(drugs)))
						goodscore = min(scoreset)
						totalnomatch = sorted(filter(lambda t: t[1] == goodscore, matchno), key=itemgetter(1, 2))
						break
					if nomatch:
						j += 1
						totalnomatch.extend(nomatch)
					if similar:
						k += 1
						totalsimilar.extend(similar)
				if j > 1:
					# 按相关性,长度由小到大排序
					totalnomatch.sort(key=itemgetter(1, 4))
					totalnomatch = totalnomatch[:5]
				if k > 1:
					# 按最小移动次数,相关性,长度由小到大排序
					totalsimilar.sort(key=itemgetter(2, 1, 4))
			# 根据用户输入词模糊匹配到1个
			else:
				totalmatch, totalnomatch, totalsimilar = search_core(newtext)

			if totalmatch:
				# if totalsimilar:
				# 	i = 0
				# 	myset = set()
				# 	for drugs in totalmatch:
				# 		myset.add(drugs[0])
				# 	for t in totalsimilar:
				# 		if not t[0] in myset:
				# 			totalmatch.append(t)
				# 			myset.add(t)
				# 			i += 1
				# 			if i >= show_num:
				# 				break;
				return totalmatch
			elif totalnomatch:
				# 显示权重评分等信息
				if isdetail:
					if totalsimilar:
						i = 0
						myset = set(m[0] for m in totalnomatch)
						for t in totalsimilar:
							if not t[0] in myset:
								totalnomatch.append(t)
								myset.add(t)
								i += 1
								if i >= show_num:
									break
					return totalnomatch
				# 不显示权重评分等信息
				else:
					mylist = [m[0] for m in totalnomatch]
					if totalsimilar:
						i = 0
						for t in totalsimilar:
							if not t[0] in mylist:
								mylist.append(t[0])
								i += 1
								if i >= show_num:
									break
					return mylist
			else:
				# 显示权重评分等信息
				if isdetail:
					return totalsimilar
				# 不显示权重评分等信息
				else:
					if totalsimilar:
						return [m[0] for m in totalsimilar]
	return None


def matchfrommongodb(tokenizer_all):
	# getlist = mongodb_utils.get_list()
	getlist = mongodb_utils.get_list({"currentTime": {"$gt": 1494664001430}})
	# getlist = mongodb_utils.get_list({"_id":ObjectId("5916c2bd3c95966d4b201a68")})
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
		text = " ".join(text.split()).lower()
		keywordsset = tokenizer_all.cutwkz_set(text)
		if keywordsset:
			# text = ""
			right.add("{0}\t{1}\t{2}".format(row["_id"], text, keywordsset))
			i += 1
		# right.add("{0}\t{1}".format(row["_id"], keywordsset))
		else:
			error.add(text)
		# if i > 100:
		# 	break
	# IOUtils.my_write(path_error,error)
	path_right = os.path.join("..", "wkztarget", "drugandcompany_right_drug.xls")
	IOUtils.my_write(path_right, right)


if __name__ == '__main__':
	writedict(isfuzzymatch=True, isdiscover=False, readcache=True, returntype=0)
	loadfuzzydict()
	# 本机只能通过127.0.0.1或者localhost可访问,其它机子只能通过192.168.2.135可以访问(默认是5000)
	app.run(host='0.0.0.0', port=5000, debug=True)

	# tokenizer_all = jieba.Tokenizer(jieba_dict_path)
	# matchfrommongodb(tokenizer_all)


	# begin=time.time()
	# print(search_debug_details("阿莫西",isdetail=True))
	# end=time.time()
	# print(end-begin)
	# print(search_debug_details("碘苯"))
	# amxl amlz	am tt tn
	print("\nover")
