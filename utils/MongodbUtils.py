#!/usr/bin/python
# -*- coding:utf-8 -*-

from pymongo import MongoClient

# 连接对象
_connection = MongoClient("192.168.1.136", 27017)
# 数据库
_db = _connection["spider"]
# 表
_collection = None


def set_connection(host,port):
	global _connection
	_connection=MongoClient(host, port)

def set_connection(dbname: str):
	global _db
	_db = _connection[dbname]

def set_collection(collectionname: str):
	global _collection
	_collection = _db[collectionname]
	return _collection

def get_collection():
	return _collection

def insert(value):
	"""
	添加单条数据到表中
	:param value:插入数据(数据是dict类型)
	:return:
	"""
	# user = {"name": "cui", "age": "10"}
	_collection.insert(value)


def insertbulk(value):
	"""
	同时添加多条数据到表中
	:param value: 插入集合(集合元素是dict类型)
	:return:
	"""
	# users = [{"name": "cui", "age": "9"}, {"name": "cui", "age": "11"}]
	_collection.insert(value)


def getone(search=None):
	"""
	查询单条记录
	:param search:查询参数(参数是dict类型),为空则查询第一条
	:return:
	"""
	if search:
		# return collection.find({"name": "1"})
		return _collection.find_one(search)
	return _collection.find_one()


def get_list(search=None):
	"""
	查询所有记录
	:param search: 查询参数(参数是dict类型),为空则查询全部
	:return:
	"""
	if search:
		# return collection.find({"name": "1"})
		return _collection.find(search)
	return _collection.find()


def getcount(search=None):
	"""
	查询表中数据条数
	:param search: 查询参数(参数是dict类型),为空则查询全部
	:return:
	"""
	if search:
		return _collection.count(search)
	return _collection.count()


# 高级查询
# collection.find({"age": {"$gt": "10"}}).sort("age"):


# 查看db下的所有集合
# db.collection_names()