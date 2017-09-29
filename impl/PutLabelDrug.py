#!/usr/bin/python3.5
# -*- coding:utf-8 -*-


import os, sys, re, time

sys.path.append('/home/esuser/NLP35')

import pypinyin

from impl import SearchImpl, PutLabelCore
from impl.PutLabelCore import MatchType
from utils import CollectionUtils, RegexUtils, StringUtils

# 中文模糊拼音
py_fuzzy_dict = {"c": "ch", "s": "sh", "z": "zh", "l": "n", "f": "h", "r": "l", "an": "ang", "en": "eng", "in": "ing", "ian": "iang", "uan": "uang", "ch": "c", "sh": "s", "zh": "z", "n": "l", "h": "f", "l": "r", "ang": "an", "eng": "en", "ing": "in", "iang": "ian", "uang": "uan"}
py_fuzzy_set = {"c", "s", "z", "f", "l", "r", "an", "en", "in", "ian", "uan"}

sql_discover_list = [
	"select code,standard_name,simplified_standard_name,bridging_name,inn_cn,inn_en,alternative_inn,active_ingredient_cn,active_ingredient_en,alternative_active_ingredient_name,trade_name_en,trade_name_cn,generic_brand,investigational_code,declaration_cn from yymf_discover_drugs_name_dic "]
sql_discover_where = 'where is_delete <>1 '
# sql_discover_where += 'limit 10 '
# sql_discover_drugs += "where standard_name in ('中/长链脂肪乳C6-24')"
# sql_discover_drugs += "where standard_name like '%阿莫西林%'"
sql_database_list = ["select standard_name,inn_cn,active_ingredient_cn,alternative_name from yymf_drugs_name_dic ",
					 "select inn_cn,standard_name,active_ingredient_cn,alternative_inn from yymf_drugs_name_dic ",
					 "select active_ingredient_cn,inn_cn,standard_name,alternative_active_ingredient_name from yymf_drugs_name_dic "]
sql_database_list = [
	"select standard_name,inn_cn,inn_en,active_ingredient_cn,active_ingredient_en,alternative_name,alternative_inn,alternative_active_ingredient_name from yymf_drugs_name_dic "]
sql_database_where = "where is_delete <> 1 "


# sql_database_drugs_where += " and standard_name = '羟苯丙胺/托吡卡胺'"
# sql_database_drugs_where+=" and standard_name like '%阿莫%'"



def preDeal_databasebak(rows, dict_all, isfuzzymatch, exclude_set):
	for row in rows:
		# 获取values
		setvalues = set()
		name = row[0].strip()
		if name:
			setvalues.add(name)
			namelower = name.lower()
			for i in range(1, len(row) - 1):
				name = row[i].strip()
				if name and name.lower() in namelower:
					setvalues.add(name)
		# 对key进行预处理
		try:
			strkeys = row[-1].strip()
		except:
			# print(row)
			# ('HIV(1+2型)抗体诊断检测试纸条|人类免疫缺陷病毒(HIV)I+II型抗体检测试纸条', 'HIV(1+2型)抗体诊断检测试纸条(胶体金法)', 'HIV(1+2型)抗体诊断检测试纸条', None)
			# ('谷美替尼', '谷美替尼', '谷美替尼', None)
			# ('谷美替尼', '谷美替尼', '谷美替尼片', None)
			continue
		if strkeys and setvalues:
			strkeys = strkeys.replace("（", "(").replace("）", ")")
			strkeys = re.sub(r"\(.*?\)", "", strkeys)
			strkeys = re.sub(r"\[.*?\]", "", strkeys)
			listkeys = re.split(';|\|', strkeys)
			for key in listkeys:
				key = re.sub(RegexUtils.special_chars, "", key.strip())
				if key:
					key = " ".join(key.split()).lower()
					# 模糊匹配则添加首字母作为key
					if isfuzzymatch:
						# 将值的拼音首字母作为key
						newkey = pypinyin.slug(key, separator="", style=pypinyin.FIRST_LETTER)
						if len(newkey) < 11:
							newkey = RegexUtils.get_word_nospecial_withspace(newkey)
							CollectionUtils.add_dict_setvalue_multi(dict_all, newkey, setvalues)
						# 将值转化为全拼音作为key
						newkey = pypinyin.slug(key, separator="")
						if len(newkey) < 20:
							newkey = RegexUtils.get_english_nospecial(newkey)
							CollectionUtils.add_dict_setvalue_multi(dict_all, newkey, setvalues)
					# 精确匹配,则去除一些有歧义的词,防止过拟合
					else:
						flag = False
						for exclude in exclude_set:
							if key in exclude:
								flag = True
								break
						if flag:
							continue
					key = RegexUtils.get_word_nospecial_withspace(key)
					CollectionUtils.add_dict_setvalue_multi(dict_all, key, setvalues)


def preDeal_core(key, exclude_set, isfuzzymatch):
	# 去前後空格
	key = StringUtils.remove_parentheses(key)
	# 去除特殊字符
	key = RegexUtils.get_word_nospecial_withspace(key)
	# 排除
	if exclude_set:
		if key in exclude_set:
			return None
	result = [key]
	# 模糊匹配则添加首字母作为key
	if isfuzzymatch:
		if RegexUtils.contain_zh(key):
			# 将值的拼音首字母作为key
			newkey = pypinyin.slug(key, separator="", style=pypinyin.FIRST_LETTER)
			if len(newkey) < 11:
				result.append(newkey)
			# 将值转化为全拼音作为key
			newkey = pypinyin.slug(key, separator="")
			if len(newkey) < 20:
				result.append(newkey)
	return result


def preDeal_database(rows, dict_all, isfuzzymatch, exclude_set):
	for row in rows:
		value = row[0].strip()
		if value:
			for i in range(1, len(row)):
				keys = StringUtils.strip_and_lower_split_multiple(row[i], ";|\|")
				for key in keys:
					result = preDeal_core(key, exclude_set, isfuzzymatch)
					if result:
						for key in result:
							CollectionUtils.add_dict_setvalue_single(dict_all, key, value)


def preDeal_discover(rows, dict_all, isfuzzymatch, exclude_set):
	# 遍历出来的key是用来做为value
	valueother = set()
	valueset = set()
	for row in rows:
		value = row[0].strip()
		if value:
			valueother.clear()
			valueset.clear()
			for i in range(1, len(row)):
				key = StringUtils.strip_and_lower(row[i])
				if key:
					valueother.add(key)
					result = preDeal_core(key, exclude_set, isfuzzymatch)
					if result:
						valueset |= set(result)
						valueother.add(result[0])
			value = (value, tuple(valueother))
			for key in valueset:
				CollectionUtils.add_dict_setvalue_single(dict_all, key, value)


def split_dict(dict_all, dict_zh, dict_en, isfuzzymatch):
	new_dict = {}
	for key in dict_all:
		keylen = len(key)
		# 判断是否全部数字或者长度大于30
		if key.isdigit() or keylen > 30:
			continue
		elif RegexUtils.contain_zh(key):
			if keylen < 21 and keylen > 1:
				valueset = dict_all[key]
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
			dict_en[key] = dict_all[key]
			new_dict[key] = dict_all[key]
	return new_dict


def match_fuzzy(new_dict, dict_zh, dict_en):
	# 这里先升序
	zhlist = list(dict_zh.items())
	zhlist.sort(key=lambda t: len(t[0]), reverse=False)
	zhlist = SearchImpl.remove_multi_drug(zhlist)
	# 重新赋值
	dict_zh = dict(zhlist)
	new_dict = dict(dict_zh, **dict_en)
	return new_dict, dict_zh, dict_en


def writedict(isdiscover=True, iswritedict=True, isfuzzymatch=False, readcache=False, returntype=0):
	return PutLabelCore.writedict(MatchType.drug, ("chinacity.txt", "exclude_drug.txt"),
								  [sql + sql_discover_where for sql in sql_discover_list], preDeal_discover,
								  [sql + sql_database_where for sql in sql_database_list], preDeal_database, split_dict,
								  match_fuzzy, None, isdiscover=isdiscover, iswritedict=iswritedict,
								  isfuzzymatch=isfuzzymatch, readcache=readcache, returntype=returntype)


if __name__ == '__main__':
	readcache = False
	# dict_database_drug, jieba_dict_database_drug = writedict(isdiscover=False, readcache=readcache)
	dict_discover_drug, jieba_dict_discover_drug = writedict(isdiscover=True, readcache=readcache)
	print("over")
