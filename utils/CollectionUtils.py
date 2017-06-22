#!/usr/bin/python3.5
# -*- coding:utf-8 -*-

def add_dict_setvalue_single(my_dict:dict, key, value):
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
		my_dict[key] = values
	else:
		my_dict[key] = set([value])


def add_dict_setvalue_multi(my_dict:dict, key, value:set):
	"""
	将key,value添加到dict中.如果key存在,则value添加到对应值的set集合中;如果key不存在,则value转化为set集合再进行添加
	:param my_dict:
	:param key:
	:param value:value是一个set集合对象
	:return:None
	"""
	if key in my_dict:
		values = my_dict[key]
		newvalues=values | value
		my_dict[key] = newvalues
	else:
		my_dict[key] = value

