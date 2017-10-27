#!/usr/bin/python3.5
# -*- coding:utf-8 -*-

"""
静姐中 匹配通用名
"""
import os, sys, re, time

sys.path.append("/home/esuser/NLP35")
import jieba, math
import numpy as np
import pandas as pd
from gensim.models import Word2Vec
from nltk import FreqDist

from utils import IOUtils
from utils import RegexUtils
from utils import StringUtils

try:
	import cPickle as pickle  # 序列化
except ImportError:
	import pickle

name_dict = "所有分子(1).xlsx"
name_dict_new = "{}{}".format("new_comname_", name_dict)
name_dict_temp = "drug_nct_dict_temp.pkl"
name_dict_dealed = "drug_nct_dict_dealed.pkl"

field_dict_distinct = "Molecule"

path_dict = IOUtils.get_path_sources(name_dict)
path_dict_new = IOUtils.get_path_target(name_dict_new)
path_dict_temp = IOUtils.get_path_target(name_dict_temp)
path_dict_dealed = IOUtils.get_path_target(name_dict_dealed)

name_source = "所有分子(1).xlsx"
name_source_new = "{}{}".format("new_source_", name_source)
name_source_result = "{}{}".format("result_", name_source)

field_source_distinct = "药品标准名"

path_source = IOUtils.get_path_sources(name_source)
path_source_new = IOUtils.get_path_target(name_source_new)
path_source_result = IOUtils.get_path_target(name_source_result)


def predeal(txt):
	# 替换中文字符为英文字符
	txt = StringUtils.replace_key(txt, RegexUtils.dict_zh_to_en_special_chars)
	# 提取括号里面内容
	tuple = RegexUtils.match(txt, *RegexUtils.set_match_special)
	ls = tuple[1]
	# 去掉括号【这里不用去掉，後面会一起去掉前後特殊字符】
	# for i, value in enumerate(ls):
	# 	ls[i] = RegexUtils.replace_diy_chars(value, "[(){}<>\[\]]+", "")
	# 合并成为一个集合
	ls.insert(0, tuple[0])
	# 替换一些字符为空格,并按空格切分,重新组合为集合
	result = []
	for value in ls:
		value = RegexUtils.replace_diy_chars(value, "[、+/]+", " ")
		# ,旁边如果有空格则去掉, 否则替换成空格
		if "," in value:
			while len(value) > 0 and value[0] == ",":
				value = value[1:]
			while len(value) > 0 and value[-1] == ",":
				value = value[:-1]
			if "," in value:
				value = value.replace(",", " ")
		result += value.split()
	# 去除开始和结束字符中的特殊字符
	for i, value in enumerate(result):
		while len(value) > 0 and not RegexUtils.re_wkz_all.findall(value[0]):
			value = value[1:]
		while len(value) > 0 and not RegexUtils.re_wkz_all.findall(value[-1]):
			value = value[:-1]
		value = RegexUtils.get_diy(value, RegexUtils.re_wkz_all_diy)
		result[i] = value
	# 获取长度不为空的元素
	temp = []
	for w in result:
		if w and w not in temp:
			temp.append(w)
	return temp


dict_replace1 = {"ⅰ": "i", "ⅱ": "ii", "ⅲ": "iii", "ⅳ": "iv", "ⅴ": "v", "ⅵ": "vi", "ⅶ": "vii", "ⅷ": "viii", "ⅸ": "ix", "ⅹ": "x", "ⅺ": "xi", "ⅻ": "xii"}
dict_replace2 = {"γ": "y", "ε": "e", "ι": "i", "κ": "k", "μ": "u", "ν": "v", "ο": "o", "ρ": "p", "τ": "t", "υ": "u", "χ": "x", "ω": "w"}


def deal(path, sheetname, field, path_new, readcache=True):
	if readcache and IOUtils.exist_path(path_new):
		mysource = pd.read_excel(path_new)
	else:
		mysource = pd.read_excel(path, sheetname=sheetname)
		mysource.dropna(axis=0, how="any", inplace=True)
		mysource.drop_duplicates(field, inplace=True)
		mysource[field] = mysource[field].astype(str)
		# 对某列全部行操作:去前後空格,转小写,替换罗马字符,替换希腊字符
		mysource[field] = mysource[field].map(
			lambda x: StringUtils.replace_key(StringUtils.strip_and_lower(x), dict_replace1, dict_replace2))
		# 删除前面设置为空的行
		mysource.dropna(axis=0, how="any", inplace=True)
		# 去重
		mysource.drop_duplicates(field, inplace=True)
		# index:前面的序号是否写到excel
		mysource.to_excel(path_new, index=False)
	return mysource


readcache = True
df_dict = deal(path_dict, 1, field_dict_distinct, path_dict_new, readcache)
# print(df_dict.shape)# (582, 1)
df_source = deal(path_source, 0, field_source_distinct, path_source_new, readcache)
# print(df_source.shape)# (9856, 1)

last_strs = set()
result = []
current_col_len = 1
for i, row in df_source.iterrows():
	sou = row[0]
	df1 = df_dict[df_dict[field_dict_distinct].map(len) <= len(sou)]
	result.clear()
	for ii, row2 in df1.iterrows():
		ls = row2[0].split("/")
		s = sou;
		flag = True
		for v in ls:
			if v in s:
				s = s.replace(v, "")
			else:
				flag = False
				break
		if flag:
			last_strs.add(s)
			# result.append("{}({})".format(row2[0], s))
			result.append(row2[0])

	len1 = len(result)
	if len1 > 0:
		# 有多列的情况,则去重有包含的情况
		if len1 > 1:
			result.sort(key=len)
			temp = []
			for index in range(0, len1 - 1):
				cur = result[index]
				flag = True
				for index2 in range(index + 1, len1):
					if cur in result[index2]:
						flag = False
						break
				if flag:
					temp.append(cur)
			temp.append(result[-1])
			result = temp
		# 添加第一列为原字段
		result.insert(0, row[0])
		# 重新获取要插入的数据长度
		len1 = len(result)
		# 插入的数据比原來df的列数还多,则新建列
		if len1 > current_col_len:
			for index in range(current_col_len, len1):
				df_source["通用名" + str(index)] = None
			current_col_len = len1
		# 插入的数据比df的列数还少,则补充到和列数一样多
		if len1 < current_col_len:
			for index in range(len1, current_col_len):
				result.append(None)
		df_source.loc[i] = tuple(result)

df_source.to_excel(path_source_result, index=False)
print(last_strs)
