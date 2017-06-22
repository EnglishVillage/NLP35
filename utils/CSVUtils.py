#!/usr/bin/python3.5
# -*- coding:utf-8 -*-

import csv



def read_dict(path, encoding="utf-8"):
	"""
	读取csv文件返回dict格式的list
	:param path:
	:param encoding:
	:return:csv文件必须包含标题,但数据不包含标题
	[{'title': 'Auxilio Announces New Chief Operating Officer', 'companyName': 'Auxilio, Inc.'}]
	"""
	with open(path, encoding=encoding) as csv_file:
		csvrows = csv.DictReader(csv_file)
		ls = []
		for row in csvrows:
			ls.append(row)
		return ls


def read_list(path, encoding="utf-8"):
	"""
	读取csv文件返回list格式的list
	:param path:
	:param encoding:
	:return:csv文件不要有标题,数据中不包含标题
	['Patient Safety Movement Foundation', 'http://www.businesswire.com/news/home/20170405005495/nl']
	"""
	with open(path, encoding=encoding) as csv_file:
		csvrows = csv.reader(csv_file)
		ls = []
		for row in csvrows:
			ls.append(row)
	return ls


def write_dict(path, names, ls):
	"""
	写入dict格式的list数据到csv文件
	:param path:
	:param names:标题的集合:["first", "last"]
	:param ls:dict格式的集合:[{"first": "wang", "last": "kunzao"}]
	:return:None
	"""
	# 要设置newline不然写入一行,会多出一个换行
	with open(path, mode="w", encoding="utf-8", newline="") as csv_file:
		writer = csv.DictWriter(csv_file, fieldnames=names)
		writer.writeheader()
		for row in ls:
			writer.writerow(row)


def write_list(path,ls):
	"""
	写入list格式的list数据到csv文件
	:param path:
	:param names:标题的集合:["first", "last"]
	:param ls:list格式的集合:["wang", "kunzao"]
	:return:None
	"""
	# 要设置newline不然写入一行,会多出一个换行
	with open(path, mode="w", encoding="utf-8",newline="") as csv_file:
		writer=csv.writer(csv_file,dialect="excel")
		# 标题和数据格式都是一样的
		for row in ls:
			writer.writerow(row)


