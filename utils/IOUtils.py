#!/usr/bin/python3.5
# -*- coding:utf-8 -*-

import os, sys, re, time

from utils import OtherUtils, JiebaUtils

try:
	import json  # python >= 2.6
except ImportError:
	import simplejson as json  # python <= 2.5


def get_path_target(filename, *dirs):
	"""
	根据文件名获取本项目target文件路径
	:param filename:文件名
	:return:
	"""
	path = os.path.join("..", "wkztarget", filename)
	if dirs:
		index = path.index(filename)
		start = path[:index]
		middle = ""
		split = path[index - 1]
		for dir in dirs:
			middle += dir + split
		return start + middle + filename
	return path


def get_path_sources(filename, *dirs):
	"""
	根据文件名获取本项目sources文件相对路径
	:param filename:文件名
	:return:
	"""
	path = os.path.join("..", "sources", filename)
	if dirs:
		index = path.index(filename)
		start = path[:index]
		middle = ""
		split = path[index - 1]
		for dir in dirs:
			middle += dir + split
		return start + middle + filename
	return path


def get_path_sources_absolute(filename):
	"""
	根据文件名获取本项目sources文件绝对路径
	:param filename:文件名
	:return:
	"""
	return os.path.abspath(os.path.join("..", "sources", filename))


def exist_sources(filename,*dirs):
	return os.path.exists(get_path_sources(filename, *dirs))

def exist_target(filename,*dirs):
	return os.path.exists(get_path_target(filename, *dirs))

def exist_path(path):
	return os.path.exists(path)


def my_write(path, data):
	"""
	写入文件
	:param path:文件路径
	:param data:集合类型数据
	:return:None
	"""
	with open(path, "w", encoding="utf-8") as f:
		for value in data:
			f.write("{0}\n".format(value))


def my_write_target(filename, data):
	"""
	写入文件
	:param path:文件路径
	:param data:集合类型数据
	:return:None
	"""
	with open(get_path_target(filename), "w", encoding="utf-8") as f:
		if isinstance(data, dict):
			for key in data:
				f.write("{0}\t{1}\n".format(key, data[key]))
		else:
			for value in data:
				f.write("{0}\n".format(value))


def my_write_match_dict(new_dict, dict_zh, dict_en, path_zh, path_en, jieba_dict_path_all, jieba_dict_path_zh,
						jieba_dict_path_en, iswritedict):
	"""
	将词库dict类型写入到文件中
	:param path:
	:param mydict:
	:return:
	"""
	if iswritedict:
		mylist = list(dict_zh.items())
		mylist.sort(key=lambda t: len(t[0]), reverse=True)
		my_write(path_zh, mylist)
		mylist = list(dict_en.items())
		mylist.sort(key=lambda t: len(t[0]), reverse=True)
		my_write(path_en, mylist)
		# 写入结巴字典
		dict_set_all = set(new_dict.keys())
		JiebaUtils.writefile(jieba_dict_path_all, dict_set_all)
		dict_set_zh = set(dict_zh.keys())
		JiebaUtils.writefile(jieba_dict_path_zh, dict_set_zh)
		dict_set_en = set(dict_en.keys())
		JiebaUtils.writefile(jieba_dict_path_en, dict_set_en)
	else:
		zhls = list(dict_zh.keys())
		zhls.sort(key=lambda t: len(t), reverse=True)
		my_write(path_zh, zhls)
		enls = list(dict_en.keys())
		enls.sort(key=lambda t: len(t), reverse=True)
		my_write(path_en, enls)


def my_read_source(filename, data=[]):
	"""
	读取文件,一行一行读取作为字符串
	:param path:文件路径
	:param data:默认返回list集合
	:return:list或者set集合,默认返回list集合
	"""
	with open(get_path_sources(filename), "r", encoding="utf-8") as f:
		if isinstance(data, list):
			for line in f.readlines():
				if line:
					data.append(line.strip())
		elif type(data) is set:
			for line in f.readlines():
				if line:
					data.add(line.strip())
	return data


def my_read_target(filename, data=[]):
	"""
	读取文件,一行一行读取作为字符串
	:param path:文件路径
	:param data:默认返回list集合
	:return:list或者set集合,默认返回list集合
	"""
	with open(get_path_target(filename), "r", encoding="utf-8") as f:
		if isinstance(data, list):
			for line in f.readlines():
				if line:
					data.append(line.strip())
		elif type(data) is set:
			for line in f.readlines():
				if line:
					data.add(line.strip())
	return data


def my_read_tuple_set(path, mydict):
	"""
	读取tuple【(key,set())】类型的文件
	:param path:
	:param mydict:
	:return: dict类型
	"""
	with open(path, "r", encoding="utf-8") as f:
		for line in f.readlines():
			if line:
				newline = line[2:-4]
				ls = newline.split("', {'")
				try:
					mydict[ls[0]] = set(ls[1].split("', '"))
				except:
					ls = newline.split(", {")
					key = ls[0][:-1]
					setvals = set()
					vals = ls[1].split(", ")
					length = len(vals)
					for i in range(length):
						if i < length - 1:
							setvals.add(vals[i][1:-1])
						else:
							setvals.add(vals[i][1:])
					mydict[key] = setvals


def my_read_match_dict_set(dict_zh, dict_en, path_zh, path_en, jieba_dict_path_all, jieba_dict_path_zh,
						   jieba_dict_path_en, returntype):
	"""
	读取文件中tuple【(key,set())】类型的字符串转化为dict类型
	:param dict_zh:
	:param dict_en:
	:param path_zh:
	:param path_en:
	:param jieba_dict_path_all:
	:param jieba_dict_path_zh:
	:param jieba_dict_path_en:
	:param returntype:
	:return:
	"""
	my_read_tuple_set(path_zh, dict_zh)
	my_read_tuple_set(path_en, dict_en)
	if returntype == 0:
		dict_all = dict(dict_zh, **dict_en)
		return (dict_all, jieba_dict_path_all)
	elif returntype == 1:
		return (dict_zh, jieba_dict_path_zh)
	elif returntype == 2:
		return (dict_en, jieba_dict_path_en)


def my_read_tuple_dict(path, mydict):
	"""
	读取tuple【(key,set())】类型的文件
	:param path:
	:param mydict:
	:return: dict类型
	"""
	with open(path, "r", encoding="utf-8") as f:
		for line in f.readlines():
			if line:
				newline = line[2:-2]
				ls = newline.split("', {'")
				if (len(ls) == 2):
					json.loads(ls[1])


def my_read_match_dict_dict(dict_zh, dict_en, path_zh, path_en, jieba_dict_path_all, jieba_dict_path_zh,
							jieba_dict_path_en, returntype):
	"""
	读取文件中tuple【(key,set())】类型的字符串转化为dict类型
	:param dict_zh:
	:param dict_en:
	:param path_zh:
	:param path_en:
	:param jieba_dict_path_all:
	:param jieba_dict_path_zh:
	:param jieba_dict_path_en:
	:param returntype:
	:return:
	"""
	my_read_tuple_dict(path_zh, dict_zh)
	my_read_tuple_dict(path_en, dict_en)
	if returntype == 0:
		dict_all = dict(dict_zh, **dict_en)
		return (dict_all, jieba_dict_path_all)
	elif returntype == 1:
		return (dict_zh, jieba_dict_path_zh)
	elif returntype == 2:
		return (dict_en, jieba_dict_path_en)


def load_exclude(filenames, myset=set()):
	if filenames:
		for name in filenames:
			my_read_source(name, myset)
		if "" in myset:
			myset.remove("")
		if None in myset:
			myset.remove(None)
