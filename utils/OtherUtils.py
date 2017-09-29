#!/usr/bin/python3.5
# -*- coding:utf-8 -*-

import os, sys, re, time
from bs4 import BeautifulSoup
from nltk.corpus import stopwords

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
from utils import IOUtils

try:
	import cPickle as pickle  # 序列化
except ImportError:
	import pickle

# 将本文件路径告诉环境
# sys.path.append(os.path.normpath(os.path.join(os.getcwd(), __file__)))

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


def review_to_sentence(review: str, tokenizer, remove_stopwords=False):
	'''
	将评论段落转换为句子，返回句子列表，每个句子由一堆词组成
	'''
	# python3.5不需要转化
	# raw_sentences = tokenizer.tokenize(review.strip().decode('utf-8'))
	raw_sentences = tokenizer.tokenize(review.strip())

	sentences = []
	for raw_sentence in raw_sentences:
		if len(raw_sentence) > 0:
			# 获取句子中的词列表
			sentences.append(review_to_wordlist(raw_sentence, remove_stopwords))
	return sentences


"With all this stuff going down at the moment with MJ i\'ve started listening to his music, watching the odd documentary here and there, watched The Wiz and watched Moonwalker again. Maybe i just want to get a certain insight into this guy who i thought was really cool in the eighties just to maybe make up my mind whether he is guilty or innocent. Moonwalker is part biography, part feature film which i remember going to see at the cinema when it was originally released. Some of it has subtle messages about MJ's feeling towards the press and also the obvious message of drugs are bad m'kay.<br /><br />Visually impressive but of course this is all about Michael Jackson so unless you remotely like MJ in anyway then you are going to hate this and find it boring. Some may call MJ an egotist for consenting to the making of this movie BUT MJ and most of his fans would say that he made it for the fans which if true is really nice of him.<br /><br />The actual feature film bit when it finally starts is only on for 20 minutes or so excluding the Smooth Criminal sequence and Joe Pesci is convincing as a psychopathic all powerful drug lord. Why he wants MJ dead so bad is beyond me. Because MJ overheard his plans? Nah, Joe Pesci's character ranted that he wanted people to know it is he who is supplying drugs etc so i dunno, maybe he just hates MJ's music.<br /><br />Lots of cool things in this like MJ turning into a car and a robot and the whole Speed Demon sequence. Also, the director must have had the patience of a saint when it came to filming the kiddy Bad sequence as usually directors hate working with one kid let alone a whole bunch of them performing a complex dance scene.<br /><br />Bottom line, this movie is for people who like MJ on one level or another (which i think is most people). If not, then stay away. It does try and give off a wholesome message and ironically MJ\'s bestest buddy in this movie is a girl! Michael Jackson is truly one of the most talented people ever to grace this planet but is he guilty? Well, with all the attention i\'ve gave this subject....hmmm well i don\'t know because people can be different behind closed doors, i know this for a fact. He is either an extremely nice but stupid guy or one of the most sickest liars. I hope he is not the latter."


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
		sentences += review_to_sentence(review, tokenizer, remove_stopwords)
	return sentences


def save_fit_model(filename: str, model):
	"""
	保存模型到默认目录(./wkztarget/)下指定文件
	:param filename:保存的文件名
	:param model:模型对象
	:param defaultPath:保存路径
	:return:空
	"""
	path = IOUtils.get_path_target(filename)
	with open(path, 'wb') as f:
		pickle.dump(model, f)


def load_fit_model(filename: str):
	"""
	从默认目录(./wkztarget/)下指定文件载入模型
	:param filename: 保存的文件名
	:param defaultPath: 保存路径
	:return: 模型对象
	"""
	path = IOUtils.get_path_target(filename)
	return pickle.load(open(path, 'rb'))
