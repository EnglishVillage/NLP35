#!/usr/bin/python
# -*- coding:utf-8 -*-

import os, sys, re, time

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

def my_writedict(path, data):
	"""
	写入文件
	:param path:文件路径
	:param data:dict类型数据
	:return:None
	"""
	# path = os.path.join("..", "sources", "createdict.txt")
	with open(path, "w", encoding="utf-8") as f:
		for key in data:
			f.write("{0}\t{1}\n".format(key,data[key]))

def my_read(path,data=[]):
	"""
	读取文件
	:param path:文件路径
	:param data:默认返回list集合
	:return:list或者set集合
	"""
	# path = os.path.normpath(os.path.join(os.getcwd(), createdictpath))
	with open(path, "r",encoding="utf-8") as f:
		if isinstance(data,list):
			for line in f.readlines():
				if line:
					data.append(line.strip())
		elif type(data) is set:
			for line in f.readlines():
				if line:
					data.add(line.strip())
	return data
