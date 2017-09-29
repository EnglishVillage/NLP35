#!/usr/bin/python3.5
# -*- coding:utf-8 -*-

"""
	静姐,对药品进行模糊匹配结果
"""

import os, sys, re, time

sys.path.append('/home/esuser/NLP35')
import pyodbc
from utils import OtherUtils, IOUtils, CollectionUtils, RegexUtils
from impl import SearchImpl


if __name__ == '__main__':
	SearchImpl.writedict()
	SearchImpl.loadfuzzydict()

	filepath = IOUtils.get_path_sources_absolute("产品规格.mdb")
	conn_str = ('DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + filepath + ';')
	cnxn = pyodbc.connect(conn_str)
	cursor = cnxn.cursor()

	# for table_info in cursor.tables(tableType='TABLE'):
	#     print(table_info.table_name)

	# row=cursor.execute("select * from 查询").fetchone()
	# print(row)

	cursor.execute("select * from 查询")
	rows = cursor.fetchall()
	i = 0
	createdictpath = IOUtils.get_path_target("searchdrugtest.txt")
	with open(createdictpath, "w", encoding="utf-8") as f:
		for row in rows:
			# print(row[0]+";"+row[1])
			f.write("%s\t%s\n" % (row[0], SearchImpl.search_debug(row[0])))
		# print("%s\t%s" %(row[0],SearchImpl.search_debug(row[0])))
		# i+=1
		# if i>10:
		# 	break
