#!/usr/bin/python3.5
# -*- coding:utf-8 -*-

# 将key,value添加到dict中.如果key存在,则value添加到对应值的set集合中;如果key不存在,则value转化为set集合再进行添加
def add_dict_setvalue_single(my_dict: dict, key, value):
	"""
	将key,value添加到dict中.如果key存在,则value添加到对应值的set集合中;如果key不存在,则value转化为set集合再进行添加
	:param my_dict:
	:param key:
	:param value:value是一个非集合对象
	:return:None
	"""
	if key in my_dict:
		values = my_dict[key]
		values.add(value)
	else:
		my_dict[key] = set([value])

# 将key,value添加到dict中.如果key存在,则value添加到对应值的set集合中;如果key不存在,则value转化为set集合再进行添加
def add_dict_setvalue_multi(my_dict: dict, key, value: set):
	"""
	将key,value添加到dict中.如果key存在,则value添加到对应值的set集合中;如果key不存在,则value转化为set集合再进行添加
	:param my_dict:
	:param key:
	:param value:value是一个set集合对象
	:return:None
	"""
	if key in my_dict:
		values = my_dict[key]
		newvalues = values | value
		my_dict[key] = newvalues
	else:
		my_dict[key] = value

# 将key,value添加到dict中.如果key存在,则value和Oldvalue会合并,但不会覆盖
def add_dict_setvalue_multi_map(my_dict: dict, key, value: map):
	"""
	将key,value添加到dict中.如果key存在,则value和Oldvalue会合并,但不会覆盖
	:param my_dict:
	:param key:
	:param value:value是一个map集合对象
	:return:None
	"""
	if key in my_dict:
		values = my_dict[key]
		my_dict[key] = dict(value, **values)
	else:
		my_dict[key] = value

# 去除list中重复元素,并返回原顺序的ls2
def distinct_list(ls):
	"""
	去除list中重复元素,并返回原顺序的ls2
	:param ls:
	:return:
	"""
	ls2 = []
	for id in ls:
		if id not in ls2:
			ls2.append(id)
	return ls2
