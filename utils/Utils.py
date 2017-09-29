#!/usr/bin/python3.5
# -*- coding:utf-8 -*-

import os, sys, re, time

sys.path.append('/home/esuser/NLP35')
import pymysql
from pymongo import MongoClient

from utils import CollectionUtils


class MysqlUtils(object):
	# 正式需要修改host和_db
	def __init__(self, host="192.168.1.136", port=3306, user="root", passwd="hblc123", _db="base_new"):
		"""
		默认构造函数
		测试:host="192.168.1.136", port=3306, user="root", passwd="hblc123", _db="base_new"
		:param host: sql连接主机
		:param port: sql端口
		:param user: 用户名
		:param passwd: 密码
		:param _db: 数据库
		"""
		self.host = host
		self.port = port
		self.user = user
		self.passwd = passwd
		self._db = _db

	def getrows(self, sql: str):
		"""
		根据sql查询返回查询列表
		:param sql: sql语句
		:return: tuple类型
		"""
		# 创建连接
		conn = pymysql.connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd, db=self._db,
							   charset='utf8')
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

	def _add_tag_set(self, myset: set, value, islower=True):
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

	def _rows_to_set(self, rows: tuple, islower=True):
		myset = set()
		for row in rows:
			if isinstance(row, tuple):
				for value in row:
					self._add_tag_set(myset, value, islower)
			else:
				self._add_tag_set(myset, row, islower)
		return myset

	def _add_tag_dict(self, mydict: dict, key, value, islower=True):
		if key and value:
			# 对key进行去前後空格和换行
			if not type(key) is str:
				key = str(key)
			key = key.strip()
			if key:
				key = key.replace("\n", "").strip()
			# 对value进行去前後空格和换行
			if not isinstance(value, str):
				value = str(value)
			value = value.strip()
			if value:
				# 只对value进行小写转化,这个value最後会作为key
				if islower:
					value = value.lower().replace("\n", "").strip()
				else:
					value = value.replace("\n", "").strip()
			if key and value:
				CollectionUtils.add_dict_setvalue_single(mydict, key, value)

	def _rows_to_dict(self, rows: tuple, islower=True):
		mydict = {}
		for row in rows:
			if isinstance(row, tuple):
				for index in range(1, len(row)):
					if row[index]:
						self._add_tag_dict(mydict, row[0], row[index], islower)
		return mydict

	def sql_to_set(self, sql: str, islower=True):
		"""
		将sql查询结果转化为set集合,用于生成字典
		:param sql:sql语句
		:param islower: 是否转化为小写,默认转化为小写
		:return:String类型的set集合
		"""
		rows = self.getrows(sql)
		return self._rows_to_set(rows, islower)

	def sql_to_dict(self, sql: str, islower=True):
		"""
		将sql查询结果转化为dict集合,用于生成字典
		:param sql:sql语句
		:param islower: 是否转化为小写,默认转化为小写
		:return:以第一列为key,set为value的dict
		"""
		rows = self.getrows(sql)
		return self._rows_to_dict(rows, islower)


class MongodbUtils(object):
	def __init__(self, collectionname, host="192.168.1.136", port=27017, dbname="spider"):
		self.connection = MongoClient(host, port)
		self.db = self.connection[dbname]
		self.collection = self.db[collectionname]

	def insert(self, value):
		"""
		添加单条数据到表中
		:param value:插入数据(数据是dict类型)
		:return:
		"""
		# user = {"name": "cui", "age": "10"}
		self.collection.insert(value)

	def insertbulk(self, value):
		"""
		同时添加多条数据到表中
		:param value: 插入集合(集合元素是dict类型)
		:return:
		"""
		# users = [{"name": "cui", "age": "9"}, {"name": "cui", "age": "11"}]
		self.collection.insert(value)

	def getone(self, search=None):
		"""
		查询单条记录
		:param search:查询参数(参数是dict类型),为空则查询第一条
		:return:
		"""
		if search:
			# return collection.find({"name": "1"})
			return self.collection.find_one(search)
		return self.collection.find_one()

	def get_list(self, search=None):
		"""
		查询所有记录(遍历的时候,通过row["content"]获取字段的值,通过row["_id"]获取ID)
		:param search: 查询参数(参数是dict类型),为空则查询全部,
		{"_id":ObjectId("5916c3243c95966d4b201b5c")}根据id查询,
		{"currentTime":{"$gt":1494664001430}}根据时间段查询
		{"name": "1"}
		:return:
		"""
		if search:
			return self.collection.find(search)
		return self.collection.find()

	def get_page(self, search=None, pageindex=1, pagesize=10):
		"""
		查询所有记录(遍历的时候,通过row["content"]获取字段的值,通过row["_id"]获取ID)
		:param search: 查询参数(参数是dict类型),为空则查询全部,{"_id":ObjectId("5916c3243c95966d4b201b5c")}根据id查询,{"currentTime":{"$gt":1494664001430}}根据时间段查询
		:return:
		"""
		if search:
			find = self.collection.find(search)
		else:
			find = self.collection.find()
		if pageindex > 1:
			find = find.skip((pageindex - 1) * pagesize)
		return find.limit(pagesize)

	def getcount(self, search=None):
		"""
		查询表中数据条数
		:param search: 查询参数(参数是dict类型),为空则查询全部
		:return:
		"""
		if search:
			return self.collection.count(search)
		return self.collection.count()

	# 高级查询
	# collection.find({"age": {"$gt": "10"}}).sort("age"):

	# 查看db下的所有集合
	# db.collection_names()
