#!/usr/bin/python
# -*- coding:utf-8 -*-

import sys
import os
import pymysql

#将本文件路径告诉环境
sys.path.append(os.path.normpath(os.path.join(os.getcwd(), __file__)))

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
	return getrowswithfull("192.168.1.136", 3306, "root", "hblc123", "base", sql)
