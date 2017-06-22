#!/usr/bin/python3.5
# -*- coding:utf-8 -*-

import os, sys, re, time

# 中文正则表达式
pattern_wkz_zh = re.compile("[\u4E00-\u9FD5]+")
# 英文正则表达式
pattern_wkz_eng = re.compile("[a-zA-Z0-9\u0370-\u03ff]+")
# 特殊字符
special_chars = '[’!"#$%&\'()*+,-./:;<=>?@，。?★☆、．…【】《》（）？“”‘’－＆！[\\]^_`{|}~]+'

def contain_zh(word):
	"""
	判断是否包含中文
	:param word:
	:return: True包含中文
	"""
	return pattern_wkz_zh.search(word)

def contain_eng(word):
	"""
	匹配是否含有大小写字母,数字,希腊字母
	:param word:
	:return:
	"""
	return pattern_wkz_eng.search(word)

def remove_special_chars(word):
	"""
	去除特殊字符
	:param word:
	:return:
	"""
	return re.sub(special_chars, "", word)

def remove_diy_chars(word,diychars):
	"""
	去除自定义字符
	:param word:
	:param diychars:"[A-Za-z0-9ó]"
	:return:
	"""
	return re.sub(diychars,"",word)