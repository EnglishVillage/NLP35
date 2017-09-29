#!/usr/bin/python3.5
# -*- coding:utf-8 -*-

# !/usr/bin/python3.5
# -*- coding:utf-8 -*-

import os, sys, re, time

sys.path.append('/home/esuser/NLP35')

from impl import PutLabelCore
from impl.PutLabelCore import MatchType
from utils import CollectionUtils, RegexUtils,StringUtils

sql_discover_list = ["select code,standard_name_cn,standard_name_en,alternative_name from yymf_discover_indication "]
sql_discover_where = "where is_delete <> 1 and indication_level > 1 "


# sql_discover_where += "and code='T03310000' "
# sql_discover_where += "limit 20 "


def preDeal_discover_core(key):
	key = StringUtils.remove_parentheses(key)
	key = RegexUtils.get_word_nospecial_withspace(key)
	return key

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
					if i > 2:
						keysarr = (w.strip() for w in key.replace("；", ";").split(";") if w.strip())
						for key in keysarr:
							key = preDeal_discover_core(key)
							if key:
								valueother.add(key)
					else:
						valueother.add(key)
						key = preDeal_discover_core(key)
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
		else:
			length = len(key)
			if RegexUtils.contain_zh(key):
				if length > 1:
					valset = dict_all[key]
					dict_zh[key] = valset
					new_dict[key] = valset
			elif length > 1 and length < 51:
				dict_en[key] = dict_all[key]
				new_dict[key] = dict_all[key]
	return new_dict


def writedict(isdiscover=True, iswritedict=True, isfuzzymatch=False, readcache=False, returntype=0):
	return PutLabelCore.writedict(MatchType.indicaton, None, [sql + sql_discover_where for sql in sql_discover_list],
								  preDeal_discover, None, None, split_dict, None, None, isdiscover=isdiscover,
								  iswritedict=iswritedict, isfuzzymatch=isfuzzymatch, readcache=readcache,
								  returntype=returntype)


if __name__ == '__main__':
	dict_discover_indication, jieba_dict_discover_indication = writedict(isdiscover=True)
	print("over")
