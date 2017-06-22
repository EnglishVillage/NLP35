#!/usr/bin/python3.5
# -*- coding:utf-8 -*-

import os, sys, re, time

from utils import OtherUtils


def get_path_target(filename):
	"""
	根据文件名获取本项目target文件路径
	:param filename:文件名
	:return:
	"""
	return os.path.join("..", "wkztarget", filename)


def get_path_sources(filename):
	"""
		根据文件名获取本项目sources文件路径
		:param filename:文件名
		:return:
		"""
	return os.path.join("..", "sources", filename)


def get_path_sources_absolute(filename):
	"""
		根据文件名获取本项目sources文件路径
		:param filename:文件名
		:return:
		"""
	# return os.path.normpath(os.path.join("..", "sources", file))
	return os.path.abspath(os.path.join("..", "sources", filename))


def my_write(path, data):
	"""
	写入文件
	:param path:文件路径
	:param data:集合类型数据
	:return:None
	"""
	# path = os.path.join("..", "sources", "createdict.txt")
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
	# path = os.path.join("..", "sources", "createdict.txt")
	with open(get_path_target(filename), "w", encoding="utf-8") as f:
		if isinstance(data, dict):
			for key in data:
				f.write("{0}\t{1}\n".format(key, data[key]))
		else:
			for value in data:
				f.write("{0}\n".format(value))


def my_read(path, data=[]):
	"""
	读取文件
	:param path:文件路径
	:param data:默认返回list集合
	:return:list或者set集合
	"""
	# path = os.path.normpath(os.path.join(os.getcwd(), createdictpath))
	with open(path, "r", encoding="utf-8") as f:
		if isinstance(data, list):
			for line in f.readlines():
				if line:
					data.append(line.strip())
		elif type(data) is set:
			for line in f.readlines():
				if line:
					data.add(line.strip())
	return data


def my_read_source(filename, data=[]):
	"""
	读取文件
	:param path:文件路径
	:param data:默认返回list集合
	:return:list或者set集合,默认返回list集合
	"""
	# path = os.path.normpath(os.path.join(os.getcwd(), createdictpath))
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
