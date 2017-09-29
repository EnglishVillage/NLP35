#!/usr/bin/python3.5
# -*- coding:utf-8 -*-
import os, sys, re, time
from enum import Enum

from utils import RegexUtils,IOUtils

sys.path.append('/home/esuser/NLP35')

from utils.Utils import MysqlUtils

# 正式需要修改host和_db
mysql_utils = MysqlUtils(_db="base")


def split_dict(dict_all, dict_zh, dict_en):
	new_dict = {}
	for key in dict_all:
		length = len(key)
		valset = dict_all[key]
		if RegexUtils.contain_zh(key):
			if length > 1:
				dict_zh[key] = valset
				new_dict[key] = valset
		elif length > 1:
			dict_en[key] = valset
			new_dict[key] = valset
	return new_dict


def writedict(matchtype, sql, fieldlist, match_index_exact, match_index_fuzzy, match_exact_func, match_fuzzy_func,
			  split_dict_func=split_dict, excludedictfilenames=None, iscache=False, iswritedict=True, returntype=0):
	# 字典存储路径
	tempfile = ""
	filename = "match_" + matchtype.name
	jieba_filename = "match_jieba_" + matchtype.name
	path_zh = IOUtils.get_path_target(filename + tempfile + "_zh.txt")
	path_en = IOUtils.get_path_target(filename + tempfile + "_en.txt")
	jieba_dict_path_zh = IOUtils.get_path_target(jieba_filename + tempfile + "_zh.txt")
	jieba_dict_path_en = IOUtils.get_path_target(jieba_filename + tempfile + "_en.txt")
	jieba_dict_path_all = IOUtils.get_path_target(jieba_filename + tempfile + "_all.txt")

	dict_all = {}
	dict_zh = {}
	dict_en = {}

	# 判断缓存文件是否存在
	isexist = os.path.exists(path_zh)
	if iscache and isexist:
		return IOUtils.my_read_match_dict_dict(dict_zh, dict_en, path_zh, path_en, jieba_dict_path_all,
											   jieba_dict_path_zh, jieba_dict_path_en, returntype)
	else:
		exclude_set = set()
		# 加载排除字典
		IOUtils.load_exclude(excludedictfilenames, exclude_set)

		rows = mysql_utils.getrows(sql)
		# 得到字典
		for row in rows:
			model = {}
			for i, field in enumerate(row):
				model[fieldlist[i]] = field
			# 精确匹配
			match_exact_func(row, dict_all, model, match_index_exact)
			# 模糊匹配
			match_fuzzy_func(row, dict_all, model, match_index_fuzzy)

		# 分成中英文
		new_dict = split_dict_func(dict_all, dict_zh, dict_en)

		# 写入字典,判断写入key还是写入key/value
		IOUtils.my_write_match_dict(new_dict, dict_zh, dict_en, path_zh, path_en, jieba_dict_path_all,
									jieba_dict_path_zh, jieba_dict_path_en, iswritedict)

		# 返回结果
		if returntype == 0:
			return (new_dict, jieba_dict_path_all)
		elif returntype == 1:
			return (dict_zh, jieba_dict_path_zh)
		elif returntype == 2:
			return (dict_en, jieba_dict_path_zh)


class MatchType(Enum):
	company = 1
	drug = 2
