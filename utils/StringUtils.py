#!/usr/bin/python3.5
# -*- coding:utf-8 -*-

import os, sys, re, time

sys.path.append('/home/esuser/NLP35')
from utils import RegexUtils


def replace_key(text, replace_dict):
	"""
	替换
	:param text: 被替换文本
	:param replace_dict: 要替换的dict
	:return:
	"""
	for k, v in replace_dict.items():
		text = text.replace(k, v)
	return text


def remove_parentheses(key):
	"""
	去除小括号或者中括号(如果去除完为空,则不去除)
	:param key:
	:return:
	"""
	#匹配10.2%,10.%,10%这3种
	key=RegexUtils.replace_diy_chars(key, "\\d+(\\.(\\d+)?)?%")
	key = key.replace("（", "(").replace("）", ")")
	newkey = RegexUtils.replace_diy_chars(key, "\(.*?\)")
	if newkey:
		key = newkey
	newkey = RegexUtils.replace_diy_chars(key, "\[.*?\]")
	if newkey:
		return newkey
	return key

def strip_and_lower(key):
	"""
	去除前後空格并转化为小写,将2个空格转化为1个空格
	:param key:
	:return:
	"""
	try:
		return " ".join(key.strip().lower().split())
	except:
		return ""

def strip_and_lower_split_single(key,split):
	"""
	去除前後空格并转化为小写,将2个空格转化为1个空格,最後按1个分割符进行分割
	:param key:
	:param split: 分割字符串
	:return: 分成器
	"""
	return (w.strip() for w in strip_and_lower(key).split(split) if w.strip())

def strip_and_lower_split_multiple(key,pattern):
	"""
	去除前後空格并转化为小写,将2个空格转化为1个空格,最後按多个分割符进行分割
	:param key:
	:param split: 多个分割符的正则表达式,eg:";|\|"
	:return: 分成器
	"""
	return (w.strip() for w in re.split(pattern, strip_and_lower(key)) if w.strip())

def strip_and_lower_split_multiple_list(key,pattern):
	"""
	去除前後空格并转化为小写,将2个空格转化为1个空格,最後按多个分割符进行分割
	:param key:
	:param split: 多个分割符的正则表达式,eg:";|\|"
	:return: list
	"""
	return [w.strip() for w in re.split(pattern, strip_and_lower(key)) if w.strip()]


