#!/usr/bin/python
# -*- coding:utf-8 -*-

import os, sys, re, time
from utils import OtherUtils, MysqlUtils, MongodbUtils, IOUtils,CollectionUtils

dict_dict = None


def preDeal(key: str,value, mydict):
	split = re.split(';|/', key)
	for s in split:
		CollectionUtils.add_dict_setvalue_multi(mydict,s.lstrip(),value)


def writedict():
	mydict = MysqlUtils.sql_to_dict(
		"select code,standard_name,simplified_standard_name,inn_cn,inn_en,trade_name_en,trade_name_cn,investigational_code,declaration_cn from yymf_discover_drugs_name_dic")
	global dict_dict
	dict_dict = {}
	for s in mydict:
		preDeal(s, mydict[s], dict_dict)
	mylist=list(dict_dict.items())
	mylist.sort(key=lambda t:len(t[0]),reverse=True)
	IOUtils.my_write(OtherUtils.get_target_path("drugdict.txt"), mylist)


if __name__ == '__main__':
	writedict()
	# MongodbUtils.set_collection("bb")
	# getlist = MongodbUtils.get_list()
