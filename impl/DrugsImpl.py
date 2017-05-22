#!/usr/bin/python
# -*- coding:utf-8 -*-

import os, sys, re, time
# from __future__ import print_function
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import HashingVectorizer
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans, MiniBatchKMeans

from utils import OtherUtils, TableUtils


def getdict():
	"""获取字典数据"""
	rows = TableUtils.read_xlsx(file=os.path.join("..", "sources", "药品名称字典.xlsx"), istitle=True)
	mydict = {}
	for row in rows:
		values = row[1].split(";")
		for key in values:
			key = key.lstrip()
			if key in mydict:
				codes = mydict[key]
				codes.add(row[0])
				mydict[key] = codes
			else:
				mydict[key] = set([row[0]])


def transform(dataset, n_features=1000):
	# model_name = "tfidf_drugs.pkl"
	# tfidf = TfidfVectorizer(max_df=0.5, max_features=n_features, min_df=2, use_idf=True)
	# tfidf = TfidfVectorizer(min_df=2,  # 最小支持度为2
	# 			  max_features=None, strip_accents='unicode', analyzer='word', token_pattern=r'\w{1,}',
	# 			  ngram_range=(1, 3),  # 二元文法模型
	# 			  use_idf=1, smooth_idf=1,  # 平滑idf的参数可设置大于0的数,use_idf设置为True才有效.
	# 			  sublinear_tf=1)  # 去掉英文停用词
	# tfidf.fit(dataset)
	# OtherUtils.save_fit_model(model_name, tfidf)

	model_name = "tfidf_drugs.pkl"
	tfidf = OtherUtils.load_fit_model(model_name)

	X = tfidf.transform(dataset)
	return X, tfidf


def train(X, vectorizer, true_k=10, minibatch=False, showLable=False):
	# 使用采样数据还是原始数据训练k-means，
	if minibatch:
		km = MiniBatchKMeans(n_clusters=true_k, init='k-means++', n_init=1, init_size=1000, batch_size=1000,
							 verbose=False)
	else:
		km = KMeans(n_clusters=true_k, init='k-means++', max_iter=300, n_init=1, verbose=False)
	km.fit(X)
	if showLable:
		print("Top terms per cluster:")
		order_centroids = km.cluster_centers_.argsort()[:, ::-1]
		terms = vectorizer.get_feature_names()
		print(vectorizer.get_stop_words())
		for i in range(true_k):
			print("Cluster %d:" % i, end='')
			for ind in order_centroids[i, :10]:
				print(' %s' % terms[ind], end='')
			print()
	result = list(km.predict(X))
	print('Cluster distribution:')
	print(dict([(i, result.count(i)) for i in result]))
	print("over")
	return -km.score(X)


def out():
	'''在最优参数下输出聚类结果'''
	dataset = TableUtils.read_xlsx(file=os.path.join("..", "sources", "NCT Drug（待匹配）.xlsx"), colindexes=(1,),
								   istitle=True)
	dataset=[row[0] for row in dataset if row and row[0]]
	X, vectorizer = transform(dataset, n_features=500)
	score = train(X, vectorizer, true_k=10, showLable=True) / len(dataset)
	print(score)


if __name__ == '__main__':
	# getdict()

	# rows = TableUtils.read_xlsx(file=os.path.join("..", "sources", "NCT Drug（待匹配）.xlsx"), colindexes=(1,),
	# 							sheet="clinicaltrials", istitle=True)

	out()
