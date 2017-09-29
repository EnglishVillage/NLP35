#!/usr/bin/python3.5
# -*- coding:utf-8 -*-

import os, sys, re, time

# ~！@#￥%……&*（）——+｛｝：“|《》？`-=【】；‘、、。，
# !$^()_{}:"<>?[];'\,./
# 特殊字符(无空格)
special_chars = '[!"#$%&\'()*+,-./:;<=>?@，。：★☆、．…【】〔〕《》（）？“”‘’－＆！\\^_`{|}~]+'
special_chars_space = '[ !"#$%&\'()*+,-./:;<=>?@，。：★☆、．…【】〔〕《》（）？“”‘’－＆！\\^_`{|}~]+'
# 不包含分割句子的特殊字符,例如(,.，。)
special_chars_nosplit = '["#$%&\'()*+-/<=>@★☆．…【】〔〕《》（）“”‘’－＆\\^_`{|}~]+'

dict_zh_to_en_special_chars = {"（": "(", "）": ")", "【": "[", "】": "]", "｛": "{", "｝": "}", "‘": "'", "’": "'", "“": '"', "”": '"', "《": "<", "》": ">", "，": ","}
set_match_special = ["\(.*?\)", "\[.*?\]", "\{.*?\}", "\<.*?\>"]

# 数字
reg_num = "0-9"
# 小写字母
reg_alphabet_lower = "a-z"
# 大写字母
reg_alphabet_upper = "A-Z"
# 字母
reg_alphabet = "{}{}".format(reg_alphabet_lower, reg_alphabet_upper)
# 希腊字母
reg_greek_alphabet = "\u0370-\u03ff"
# 中文
reg_chinese = "\u4E00-\u9FD5"
# 数字字母希腊字母中文
reg_all = "{}{}{}{}".format(reg_num, reg_alphabet, reg_greek_alphabet, reg_chinese)

# 中文的正则表达式
re_wkz_zh = re.compile("[\u4E00-\u9FD5]+")
# 数字,字母,希腊字母,中文的正则表达式
re_wkz_all = re.compile("[{}]+".format(reg_all))
re_wkz_all_diy = re.compile("[{}:%'.-]+".format(reg_all))
# 中英文数字空格表达式
re_wkz_word_space = re.compile("[ a-zA-Z0-9\u4E00-\u9FD5]+")
# 英文数字正则表达式
re_wkz_en = re.compile("[a-zA-Z0-9\u0370-\u03ff]+")
# 英文希腊字母数字空格正则表达式
re_wkz_en_space = re.compile("[ a-zA-Z0-9\u0370-\u03ff]+")
re_wkz_special_chars = re.compile(special_chars_space)


# word="@#{}3:1%3'A.b-cA-D.α'Λ%λ:Μ{μ}村夺甘基%地%^"
# print("".join(pattern_wkz_all_diy.findall(word)))

def contain_zh(word):
	"""
	判断是否包含中文
	:param word:
	:return: True包含中文
	"""
	return re_wkz_zh.search(word)


def contain_special_chars(word):
	"""
	判断是否包含特殊字符和空格
	:param word:
	:return: True包含
	"""
	return re_wkz_special_chars.search(word)


def contain_en(word):
	"""
	匹配是否含有大小写字母,数字,希腊字母
	:param word:
	:return:
	"""
	return re_wkz_en.search(word)


def replace_special_chars(word, repl=""):
	"""
	去除特殊字符
	:param word: 原始字符串
	:param repl: 替换後字符
	:return:
	"""
	return re.sub(special_chars, repl, word)


def replace_special_chars_nosplit(word, repl=""):
	"""
	去除特殊字符,但不去除分割句子的特殊字符,例如(,.，。)
	:param word: 原始字符串
	:param repl: 替换後字符
	:return:
	"""
	return re.sub(special_chars_nosplit, repl, word)


def replace_diy_chars(txt, pattern, repl=""):
	"""
	去除自定义字符
	:param txt:原始字符串
	:param pattern:"[A-Za-z0-9ó]","\(.*?\)"替换括号里面东西,
	:param repl: 替换後字符
	:return:
	"""
	return re.sub(pattern, repl, txt)


def get_word_nospecial(word, repl=""):
	"""
	只获取中英文数字
	:param word:
	:param repl:
	:return:
	"""
	return repl.join(re_wkz_all.findall(word))


def get_word_nospecial_withspace(word, repl=""):
	"""
	只获取中英文数字空格
	:param word:
	:param repl:
	:return:
	"""
	return repl.join(re_wkz_word_space.findall(word))


def get_english_nospecial(word, repl=""):
	"""
	只获取中文英文数字
	:param word:
	:param repl:
	:return:
	"""
	return repl.join(re_wkz_en_space.findall(word))


def get_diy(word, myre, repl=""):
	"""
	根据diy正则表达式获取
	:param word: 源字符串
	:param myre: 正则表达式
	:param repl:
	:return:
	"""
	return repl.join(myre.findall(word))


def match(txt, *set_match_special):
	"""
	正则匹配需要的字符
	:param txt:原字符串
	:param set_match_special: 正则替换的集合
	:return:
	"""
	match = []
	for pattern in set_match_special:
		match += re.findall(pattern, txt)
		txt = replace_diy_chars(txt, pattern)
	return txt, match
