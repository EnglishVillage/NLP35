#!/usr/bin/python
# -*- coding:utf-8 -*-

from pymongo import MongoClient

# 连接对象
connection = MongoClient("192.168.1.136", 27017)
# 数据库
db = connection["spider"]
# 表
collection = None


def getcollection(collectionname: str):
	global collection
	collection = db[collectionname]
	return collection


def insert(value):
	"""
	添加单条数据到表中
	:param value:插入数据(数据是dict类型)
	:return:
	"""
	# user = {"name": "cui", "age": "10"}
	collection.insert(value)


def insertbulk(value):
	"""
	同时添加多条数据到表中
	:param value: 插入集合(集合元素是dict类型)
	:return:
	"""
	# users = [{"name": "cui", "age": "9"}, {"name": "cui", "age": "11"}]
	collection.insert(value)


def getone(search):
	"""
	查询单条记录
	:param search:查询参数(参数是dict类型),为空则查询第一条
	:return:
	"""
	if search:
		# return collection.find({"name": "1"})
		return collection.find_one(search)
	return collection.find_one()


def getlist(search):
	"""
	查询所有记录
	:param search: 查询参数(参数是dict类型),为空则查询全部
	:return:
	"""
	if search:
		# return collection.find({"name": "1"})
		return collection.find(search)
	return collection.find()


def getcount(search):
	"""
	查询表中数据条数
	:param search: 查询参数(参数是dict类型),为空则查询全部
	:return:
	"""
	if search:
		return collection.count(search)
	return collection.count()


# 高级查询
# collection.find({"age": {"$gt": "10"}}).sort("age"):


# 查看db下的所有集合
# db.collection_names()
