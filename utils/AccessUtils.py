#!/usr/bin/python3.5
# -*- coding:utf-8 -*-


import pyodbc
from utils import OtherUtils, IOUtils, CollectionUtils, RegexUtils

filepath=IOUtils.get_path_sources_absolute("产品规格.mdb")
conn_str = (
    r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
    r'DBQ='+filepath+';'
    )
cnxn = pyodbc.connect(conn_str)
cursor = cnxn.cursor()

# for table_info in cursor.tables(tableType='TABLE'):
#     print(table_info.table_name)

# row=cursor.execute("select * from 查询").fetchone()
# print(row)

cursor.execute("select * from 查询")
rows = cursor.fetchall()
i=0
for row in rows:
	print(row)
	i+=1
	if i>10:
		break