#!/usr/bin/python3.5
# -*- coding:utf-8 -*-

import os, sys, re, time
from enum import Enum

sys.path.append('/home/esuser/NLP35')

from utils import IOUtils, JiebaUtils
from utils.Utils import MysqlUtils

mysql_utils = MysqlUtils()

def writedict(matchtype, excludedictfilenames, sql_discovers, preDeal_discover_func, sql_databases,
			  preDeal_database_func, split_dict_func, match_fuzzy_func, match_exact_func, isdiscover=True,
			  iswritedict=True, isfuzzymatch=False, readcache=False, returntype=0):
	"""
	读取sql并写入字典
	:param matchtype:枚举类型
	:param excludedictfilenames:排除字典的文件名称集合
	:param sql_discovers:发现的sql语句集合
	:param preDeal_discover_func:发现字典的预处理函数
	:param sql_databases:数据库的sql语句集合
	:param preDeal_database_func:数据库字典的预处理函数
	:param split_dict_func:切分成中英文函数
	:param match_fuzzy_func:模糊匹配处理函数
	:param match_exact_func:精确匹配处理函数
	:param iswritedict:是否写成字典
	:param isfuzzymatch:是否模糊匹配
	:param isdiscover:是否发现
	:param readcache:是否读取缓存
	:param returntype:返回类型:0:中英文,1:中文,2:英文
	:return:返回元组对象(字典,jieba字典路径)
	"""
	# 得到缓存文件名称
	tempfile = ""
	filename = "match_" + matchtype.name
	jieba_filename = "match_jieba_" + matchtype.name
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
	jieba_dict_path_zh = IOUtils.get_path_target(jieba_filename + tempfile + "_zh.txt")
	jieba_dict_path_en = IOUtils.get_path_target(jieba_filename + tempfile + "_en.txt")
	jieba_dict_path_all = IOUtils.get_path_target(jieba_filename + tempfile + "_all.txt")

	dict_all = {}
	dict_zh = {}
	dict_en = {}
	exclude_set = set()

	# 判断缓存文件是否存在
	isexist = os.path.exists(path_zh)
	if readcache and isexist:
		return IOUtils.my_read_match_dict_set(dict_zh, dict_en, path_zh, path_en, jieba_dict_path_all, jieba_dict_path_zh, jieba_dict_path_en, returntype)
	else:
		# 加载排除字典
		IOUtils.load_exclude(excludedictfilenames, exclude_set)

		# 预处理
		if isdiscover:
			if sql_discovers:
				for sql in sql_discovers:
					rows = mysql_utils.getrows(sql)
					preDeal_discover_func(rows, dict_all, isfuzzymatch, exclude_set)
		else:
			if sql_databases:
				for sql in sql_databases:
					rows = mysql_utils.getrows(sql)
					preDeal_database_func(rows, dict_all, isfuzzymatch, exclude_set)

		# 分成中英文
		new_dict = split_dict_func(dict_all, dict_zh, dict_en, isfuzzymatch)

		# 模糊/精确匹配处理函数
		if isfuzzymatch:
			if match_fuzzy_func:
				new_dict, dict_zh, dict_en = match_fuzzy_func(new_dict, dict_zh, dict_en)
		elif match_exact_func:
			new_dict, dict_zh, dict_en = match_exact_func(new_dict, dict_zh, dict_en)

		# 写入字典,判断写入key还是写入key/value
		IOUtils.my_write_match_dict(new_dict,dict_zh,dict_en,path_zh,path_en,jieba_dict_path_all,jieba_dict_path_zh,jieba_dict_path_en,iswritedict)

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
	indicaton = 3
	target = 4
