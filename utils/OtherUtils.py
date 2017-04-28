#!/usr/bin/python
# -*- coding:utf-8 -*-

import os,sys,re
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
# import time
# import pandas as pd
# import numpy as np
# from sklearn.feature_extraction.text import TfidfVectorizer as TFIDF
# from sklearn.naive_bayes import MultinomialNB as MNB
# from sklearn.cross_validation import cross_val_score
# from sklearn.linear_model import LogisticRegression as LR
# from sklearn.grid_search import GridSearchCV
# import gensim
# import nltk
# from gensim.models import Word2Vec
# from sklearn.naive_bayes import GaussianNB as GNB
# from sklearn.ensemble import RandomForestClassifier
try:
   import cPickle as pickle   # 序列化
except ImportError:
   import pickle

#将本文件路径告诉环境
sys.path.append(os.path.normpath(os.path.join(os.getcwd(), __file__)))

tokenizer_english = "tokenizers/punkt/english.pickle"

# stopwords={}.fromkeys([line.rstrip() for line in open("./stopwords.txt")])
# stopwords = [line.rstrip() for line in open("./stopwords.txt")]
# english_stopwords = set(stopwords)
english_stopwords = set(stopwords.words("english"))


def review_to_wordlist(str: str, remove_stopwords=False):
	"""
	把IMDB的评论转成词序列
	:param str: 要预处理的字符串
	:param remove_stopwords: 是否去掉英文停用词
	:return:预处理後的字符串集合
	"""
	# 去掉HTML标签，拿到内容
	review_text = BeautifulSoup(str, "html.parser").get_text()
	# 用正则表达式取出符合规范的部分
	review_text = re.sub("[^a-zA-Z]", " ", review_text)
	# 小写化所有的词，并转成词list
	words = review_text.lower().split()
	if remove_stopwords:
		words = [w for w in words if not w in english_stopwords]
	return (words)


def review_to_sentences(review: str, tokenizer, remove_stopwords=False):
	'''
	将评论段落转换为句子，返回句子列表，每个句子由一堆词组成
	'''
	# python3.5不需要转化
	# raw_sentences = tokenizer.tokenize(review.strip().decode('utf8'))
	raw_sentences = tokenizer.tokenize(review.strip())

	sentences = []
	for raw_sentence in raw_sentences:
		if len(raw_sentence) > 0:
			# 获取句子中的词列表
			sentences.append(review_to_wordlist(raw_sentence, remove_stopwords))
	return sentences


def get_deal_data(train):
	"""
	将DataFrame中的一列进行预处理
	:param train:是DataFrame中的一列(Series类型)
	:return:预处理过列的集合
	"""
	train_data = []
	for i in range(len(train)):
		train_data.append(' '.join(review_to_wordlist(train[i])))
	return train_data


def get_sentences_data(train, tokenizer, remove_stopwords=False):
	sentences = []
	for i, review in enumerate(train):
		sentences += review_to_sentences(review, tokenizer, remove_stopwords)
	return sentences


def save_fit_model(filename:str, model, defaultPath):
	"""
	保存模型到默认目录(./wkztarget/)下指定文件
	:param filename:保存的文件名
	:param model:模型对象
	:param defaultPath:保存路径
	:return:空
	"""
	if defaultPath:
		path = os.path.join(defaultPath, filename)
	else:
		path = os.path.join(".", "wkztarget", filename)
	with open(path, 'wb') as f:
		pickle.dump(model, f)


def load_fit_model(filename: str, defaultPath: str):
	"""
	从默认目录(./wkztarget/)下指定文件载入模型
	:param filename: 保存的文件名
	:param defaultPath: 保存路径
	:return: 模型对象
	"""
	if defaultPath:
		path = os.path.join(defaultPath, filename)
	else:
		path = os.path.join(".", "wkztarget", filename)
	return pickle.load(open(path, 'rb'))



pattern_wkz_zh = re.compile("[\u4E00-\u9FD5]+")
pattern_wkz_eng = re.compile("[a-zA-Z0-9\u0370-\u03ff]+")
def contain_zh(word):
	"""
	判断是否包含中文
	:param word:
	:return: True包含中文
	"""
	global pattern_wkz_zh
	return pattern_wkz_zh.search(word)

def contain_eng(word):
	"""
	匹配是否含有大小写字母,数字,希腊字母
	:param word:
	:return:
	"""
	return pattern_wkz_eng.search(word)
