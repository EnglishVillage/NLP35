#!/usr/bin/python3.5
# -*- coding:utf-8 -*-

import os, sys, re, time

# 中文正则表达式
pattern_wkz_zh = re.compile("[\u4E00-\u9FD5]+")
# 英文正则表达式
pattern_wkz_eng = re.compile("[a-zA-Z0-9\u0370-\u03ff]+")
# 特殊字符
special_chars = '[!"#$%&\'()*+,-./:;<=>?@，。：★☆、．…【】〔〕《》（）？“”‘’－＆！\\^_`{|}~]+'
# 不包含分割句子的特殊字符,例如(,.，。)
special_chars_nosplit = '["#$%&\'()*+-/<=>@★☆．…【】〔〕《》（）“”‘’－＆\\^_`{|}~]+'

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


def remove_special_chars(word, repl=""):
	"""
	去除特殊字符
	:param word: 原始字符串
	:param repl: 替换後字符
	:return:
	"""
	return re.sub(special_chars, repl, word)

def remove_special_chars_nosplit(word, repl=""):
	"""
	去除特殊字符,但不去除分割句子的特殊字符,例如(,.，。)
	:param word: 原始字符串
	:param repl: 替换後字符
	:return:
	"""
	return re.sub(special_chars_nosplit, repl, word)

def remove_diy_chars(word, diychars, repl=""):
	"""
	去除自定义字符
	:param word:原始字符串
	:param diychars:"[A-Za-z0-9ó]"
	:param repl: 替换後字符
	:return:
	"""
	return re.sub(diychars, repl, word)
