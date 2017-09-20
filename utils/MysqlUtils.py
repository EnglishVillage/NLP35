#!/usr/bin/python3.5
# -*- coding:utf-8 -*-

import os, sys, re, time
import pymysql
from utils import CollectionUtils

host = "192.168.1.136"
port = 3306
user = "root"
passwd = "hblc123"
_db = "base_new"


def getrowswithfull(host: str, port: int, user: str, passwd: str, db: str, sql: str):
	"""
	根据sql查询返回查询列表
	:param host: sql连接主机
	:param port: sql端口
	:param user: 用户名
	:param passwd: 密码
	:param db: 数据库
	:param sql: sql语句
	:return: 查询列表
	"""
	# 创建连接
	conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db, charset='utf8')
	# 创建游标
	cursor = conn.cursor()

	# 执行SQL，执行查询,只显示受影响行数
	effect_row = cursor.execute(sql)
	# 获取剩余结果的第一行数据
	# row_1 = cursor.fetchone()
	# 获取剩余结果前n行数据
	# row_2 = cursor.fetchmany(3)
	# 获取剩余结果所有数据
	# row_3 = cursor.fetchall()
	# 执行SQL，并返回受影响行数
	# effect_row = cursor.execute("update tb7 set pass = '123' where nid = %s", (11,))
	# 执行SQL，并返回受影响行数,执行多次
	# effect_row = cursor.executemany("insert into tb7(user,pass,licnese)values(%s,%s,%s)", [("u1","u1pass","11111"),("u2","u2pass","22222")])

	# 提交，不然无法保存新建或者修改的数据
	conn.commit()
	# 关闭游标
	cursor.close()
	# 关闭连接
	conn.close()
	return cursor.fetchall()


def getrows(sql: str):
	"""
	根据sql查询返回查询列表
	:param sql: sql语句
	:return: 查询列表
	"""
	return getrowswithfull(host=host, port=port, user=user, passwd=passwd, db=_db, sql=sql)


def _add_tag_set(myset: set, value, islower=True):
	"""
	将值转化为str并添加到set集合中
	:param set: set集合
	:param value: 值
	:return: 空
	"""
	if value is not None:
		if type(value) is str:
			value = value.strip()
			if value:
				if islower:
					value = value.lower().replace("\n", "")
				else:
					value = value.replace("\n", "")
				myset.add(value)
		else:
			if islower:
				myset.add(str(value).strip().lower())
			else:
				myset.add(str(value).strip())


def _rows_to_set(rows: tuple, islower=True):
	myset = set()
	for row in rows:
		if isinstance(row, tuple):
			for value in row:
				_add_tag_set(myset, value, islower)
		else:
			_add_tag_set(myset, row, islower)
	return myset


def _add_tag_dict(mydict: dict, key, value, islower=True):
	if key and value:
		# 对key进行去前後空格和换行
		if not type(key) is str:
			key=str(key)
		key=key.strip()
		if key:
			key=key.replace("\n","").strip()
		# 对value进行去前後空格和换行
		if not isinstance(value,str):
			value=str(value)
		value=value.strip()
		if value:
			# 只对value进行小写转化,这个value最後会作为key
			if islower:
				value=value.lower().replace("\n","").strip()
			else:
				value=value.replace("\n","").strip()
		if key and value:
			CollectionUtils.add_dict_setvalue_single(mydict, key, value)


def _rows_to_dict(rows: tuple, islower=True):
	mydict = {}
	for row in rows:
		if isinstance(row, tuple):
			for index in range(1, len(row)):
				if row[index]:
					_add_tag_dict(mydict, row[0], row[index], islower)
	return mydict


def sql_to_set(sql: str, islower=True):
	"""
	将sql查询结果转化为set集合,用于生成字典
	:param sql:sql语句
	:param islower: 是否转化为小写,默认转化为小写
	:return:String类型的set集合
	"""
	rows = getrows(sql)
	return _rows_to_set(rows, islower)


def sql_to_dict(sql: str, islower=True):
	"""
	将sql查询结果转化为dict集合,用于生成字典
	:param sql:sql语句
	:param islower: 是否转化为小写,默认转化为小写
	:return:以第一列为key,set为value的dict
	"""
	rows = getrows(sql)
	return _rows_to_dict(rows, islower)
