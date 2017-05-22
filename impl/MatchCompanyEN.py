#!/usr/bin/python
# -*- coding:utf-8 -*-

import os, sys, re, time
from operator import itemgetter

import Levenshtein
import pandas as pd
import csv
from utils import OtherUtils, MysqlUtils, MongodbUtils





stopwords = ["corp.,ltd.", "s.a.r.l.", "co.,ltd.", "s.p.a.", "s.a.s", "corp.", "inc.", "b.v.", "n.v.", "co.,", "pty.",
			 "pte.", "a/s", "co."]
stopwords2 = ["biopharmaceuticals", "biopharmaceutical", "pharmaceuticals", "pharmaceutical", "biotechnology",
			  "venture fund", "therapeutics", "farmaceutici", "laboratories", "engineering", "laboratoire",
			  "corporation", "biosciences", "bioscience", "biological", "laboratory", "healthcare", "technology",
			  "institutes", "institute", "biopharma", "biologics", "biologic", "sciences", "ventures", "partners",
			  "products", "medicine", "holdings", "venture", "science", "biology", "biotech", "limited", "company",
			  "medical", "health", "pharma", "group", "funds", "fund", "labs", "gmbh", "kgaa", "lllp", "lab", "bio",
			  "inc", "llp", "jsc", "aps", "plc", "llc", "ltd", "ag", "kg", "lp", "oy", "sa", "bv", "ab", "nv"]

path_dict = os.path.join("..", "wkztarget", "company.txt")
path_right = os.path.join("..", "wkztarget", "right.txt")
path_error = os.path.join("..", "wkztarget", "error.txt")
dict_dict = None


def preDeal(data: str):
	"""
	预处理数据
	:param data:数据
	:return:
	"""
	# 去前後空格,并按空格切割
	data = data.lstrip()
	words = data.split()
	# 去除含有特殊字符的停止词,并去除特殊字符
	words = [re.sub(OtherUtils.special_chars, "", w) for w in words if not w in stopwords]
	# 去除通用公司名称
	words = [w for w in words if not w in stopwords2]
	# 用空格连接词组
	newdata = " ".join(words)
	if newdata:
		return newdata
	return data


def writedict():
	# set_company = MysqlUtils.sqltoset("select standard_name_en,full_name_en,alternative_name,name_FDA from yymf_discover_company")
	set_company = MysqlUtils.sql_to_set("select standard_name_en,full_name_en from yymf_discover_company")
	global dict_dict
	dict_dict = dict()
	for name in set_company:
		if name in dict_dict:
			nameset = dict_dict[name]
			nameset.add(name)
			dict_dict[name] = nameset
		else:
			dict_dict[name] = set([name])
		deal = preDeal(name)
		if deal in dict_dict:
			nameset = dict_dict[deal]
			nameset.add(name)
			dict_dict[deal] = nameset
		else:
			dict_dict[deal] = set([name])

	# with open(path_dict, "w", encoding="utf-8") as f:
	# 	for name in dict_dict:
	# 		f.write(name + "\n")


# def readdict():
# 	global set_dict
# 	set_dict = set()
# 	# path = os.path.normpath(os.path.join(os.getcwd(), createdictpath))
# 	with open(path_dict, "r", encoding="utf-8") as f:
# 		# print f.read(50)
# 		# print f.readline()
# 		for line in f.readlines():
# 			# 这里可以不加判断,因为词库我已经去掉所有空行了
# 			if line:
# 				set_dict.add(line.strip())


def matchfrommongodb():
	MongodbUtils.set_collection("prnewswire")
	getlist = MongodbUtils.get_list()
	total = 0
	i = 0
	set_right = set()
	with open(path_error, "w", encoding="utf-8") as f:
		for kv in getlist:
			olddata = kv.get("companyName", None)
			if olddata:
				total += 1
				data = preDeal(olddata.lower())
				if data in dict_dict:
					# print(olddata)
					set_right.add("%s\t%s\t%s" % (olddata.lower(), data, "|".join(dict_dict[data])))
				else:
					i += 1
					f.write("%s\t%s\t%s\n" % (kv.get("_id", None), kv.get("title", None), olddata))
	with open(path_right, "w", encoding="utf-8") as f:
		for name in set_right:
			f.write(name + "\n")
	print("total: %s \tno match:%s" % (total, i))


def matchfromcsv():
	names = ["globenewswire", "prnewswire", "businesswire"]
	# names=["businesswire"]
	for name in names:
		total = 0
		i = 0
		set_right = set()
		with open(os.path.join("..", "sources", name + ".csv"), encoding="utf-8") as csv_file:
			# 读取csv文件
			# csvrows=csv.reader(csv_file)
			csvrows = csv.DictReader(csv_file)
			# 写入匹配不到的公司名
			path_error = os.path.join("..", "wkztarget", "error_{0}.csv".format(name))
			with open(path_error, mode="w", encoding="utf-8", newline="") as f:
				writer = csv.writer(f, dialect="excel")
				writer.writerow(["title", "companyName"])
				for kv in csvrows:
					olddata = kv.get("companyName", None)
					if olddata:
						total += 1
						data = preDeal(olddata.lower())
						if data in dict_dict:
							# print(olddata)
							set_right.add((olddata.lower(), data, "|".join(dict_dict[data])))
						else:
							i += 1
							writer.writerow((kv.get("title", None), olddata))
		# 写入匹配得到的公司名
		path_right = os.path.join("..", "wkztarget", "right_{0}.csv".format(name))
		with open(path_right, mode="w", encoding="utf-8", newline="") as f:
			writer = csv.writer(f, dialect="excel")
			writer.writerow(["companyName", "keyword", "ourCompanyName"])
			for name in set_right:
				writer.writerow(name)
		print("total: %s \tno match:%s" % (total, i))


def matchfromcsv2():
	# names = ["globenewswire", "prnewswire", "businesswire"]
	names = ["prnewswire", "businesswire"]
	for name in names:
		total = 0
		i = 0
		set_right = set()
		nomatch = []
		with open(os.path.join("..", "sources", name + ".csv"), encoding="utf-8") as csv_file:
			# 读取csv文件
			# csvrows=csv.reader(csv_file)
			csvrows = csv.DictReader(csv_file)
			# 写入匹配不到的公司名
			path_error = os.path.join("..", "wkztarget", "error_{0}.csv".format(name))
			with open(path_error, mode="w", encoding="utf-8", newline="") as f:
				writer = csv.writer(f, dialect="excel")
				writer.writerow(["公司名", "匹配关键字", "相似公司"])
				for kv in csvrows:
					olddata = kv.get("companyName", None)
					if olddata:
						total += 1
						data = preDeal(olddata.lower())
						if data in dict_dict:
							# print(olddata)
							set_right.add((olddata.lower(), data, "|".join(dict_dict[data])))
						else:
							i += 1
							nomatch.clear()
							for key in dict_dict:
								winkler = Levenshtein.jaro_winkler(data, key, 0.12)
								distance = Levenshtein.distance(data, key)
								ratio = Levenshtein.ratio(data, key)
								if (winkler > 0.8 or ratio > 0.4) and distance < 20:
									nomatch.append((key, winkler, distance, ratio))
							if nomatch:
								nomatch.sort(key=itemgetter(1), reverse=True)
								writer.writerow((olddata, data, "|".join([str(w) for w in nomatch[:5]])))
							else:
								writer.writerow((olddata, data, ""))
							# writer.writerow((olddata, data, ""))

		# 写入匹配得到的公司名
		path_right = os.path.join("..", "wkztarget", "right_{0}.csv".format(name))
		with open(path_right, mode="w", encoding="utf-8", newline="") as f:
			writer = csv.writer(f, dialect="excel")
			writer.writerow(["companyName", "keyword", "ourCompanyName"])
			for name in set_right:
				writer.writerow(name)
		print("total: %s \tno match:%s" % (total, i))


if __name__ == '__main__':
	writedict()
# readdict()
	matchfromcsv2()
