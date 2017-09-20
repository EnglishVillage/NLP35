#! /usr/bin/python3.5
# -*- coding:utf-8 -*-

import os, sys, re, time

sys.path.append('/home/esuser/NLP35')

import jieba
import nltk
from nltk.corpus import brown
from nltk.tokenize import word_tokenize
from nltk.stem.porter import PorterStemmer
from nltk.stem.lancaster import LancasterStemmer
from nltk.stem import SnowballStemmer
from nltk.stem.porter import PorterStemmer

# NLTK⾃带语料库
# print(brown.categories())
# # ['adventure', 'belles_lettres', 'editorial', 'fiction', 'government', 'hobbies', 'humor', 'learned', 'lore', 'mystery', 'news', 'religion', 'reviews', 'romance', 'science_fiction']
# print(len(brown.sents()))
# print(len(brown.words()))



# # 分词
# sentence = "hello, world"
# tokens = word_tokenize(sentence)
# print(tokens)

# 中文分词
# seg_list = jieba.cut("我来到北京清华大学", cut_all=True)
# print("Full Mode:", "/ ".join(seg_list))  # 全模式
# 北京/ 清华/ 清华大学/ 华大/ 大学
# seg_list = jieba.cut("我来到北京清华大学", cut_all=False)
# print("Default Mode:", "/ ".join(seg_list))  # 精确模式
#  北京/ 清华大学
# seg_list = jieba.cut("他来到了网易杭研大厦")  # 默认是精确模式
# print(", ".join(seg_list))
# seg_list = jieba.cut_for_search("小明硕士毕业于中国科学院计算所，后在日本京都大学深造")		# 搜索引擎模式
# print(", ".join(seg_list))
# 中国, 科学, 学院, 科学院, 中国科学院, 计算, 计算所




# 社交网络语言的tokenize
# tweet = 'RT @angelababy: love you baby! :D http://ah.love #168cm'
# print(word_tokenize(tweet))

# emoticons_str = r"""
#  (?:
#  [:=;] # 眼睛
#  [oO\-]? # 鼻子
#  [D\)\]\(\]/\\OpP] # 嘴
#  )"""
# regex_str = [
# 	emoticons_str,
# 	r'<[^>]+>',  # HTML tags
# 	r'(?:@[\w_]+)',  # @某人
# 	r"(?:\#+[\w_]+[\w\'_\-]*[\w_]+)",  # 话题标签
# 	r'http[s]?://(?:[a-z]|[0-9]|[$-_@.&amp;+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+',  # URLs
# 	r'(?:(?:\d+,?)+(?:\.?\d+)?)',  # 数字
# 	r"(?:[a-z][a-z'\-_]+[a-z])",  # 含有 - 和 ' 的单词
# 	r'(?:[\w_]+)',  # 其他
# 	r'(?:\S)'  # 其他
# ]
# # re.VERBOSE忽略注释及没用空格
# tokens_re = re.compile(r'(' + '|'.join(regex_str) + ')', re.VERBOSE | re.IGNORECASE)
# emoticon_re = re.compile(r'^' + emoticons_str + '$', re.VERBOSE | re.IGNORECASE)
# def tokenize(s): return tokens_re.findall(s)
# def preprocess(s, lowercase=False):
# 	tokens = tokenize(s)
# 	if lowercase:
# 		tokens = [token if emoticon_re.search(token) else token.lower() for token in tokens]
# 	return tokens
# tweet = 'RT @angelababy: love you baby! :D http://ah.love #168cm'
# print(preprocess(tweet))

# # Stemming 词⼲提取：⼀般来说，就是把不影响词性的inflection的⼩尾巴砍掉
# porter_stemmer = PorterStemmer()
# print(porter_stemmer.stem('maximum'))
# print(porter_stemmer.stem('presumably'))
# print(porter_stemmer.stem('multiply'))
# print(porter_stemmer.stem('provision'))
# # maximum
# # presum
# # multipli
# # provis
# lancaster_stemmer = LancasterStemmer()
# print(lancaster_stemmer.stem('maximum'))
# print(lancaster_stemmer.stem('presumably'))
# print(lancaster_stemmer.stem('multiply'))
# print(lancaster_stemmer.stem('provision'))
# # maxim
# # presum
# # multiply
# # provid
# snowball_stemmer = SnowballStemmer('english')
# print(snowball_stemmer.stem('maximum'))
# print(snowball_stemmer.stem('presumably'))
# print(snowball_stemmer.stem('multiply'))
# print(snowball_stemmer.stem('provision'))
# # maximum
# # presum
# # multipli
# # provis
# p = PorterStemmer()
# print(p.stem('went'))
# print(p.stem('wenting'))

# Lemmatization 词形归⼀：把各种类型的词的变形，都归为⼀个形式








