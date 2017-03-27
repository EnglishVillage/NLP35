#! /usr/bin/python
# -*- coding:utf-8 -*-

import os
import re
import numpy as np
import pandas as pd
# 解析网页
from bs4 import BeautifulSoup
# 抽取文本特征,计数
from sklearn.feature_extraction.text import CountVectorizer
# 随机森林
from sklearn.ensemble import RandomForestClassifier
# 评估矩阵
from sklearn.metrics import confusion_matrix

import nltk
from nltk.corpus import stopwords

# from sklearn.naive_bayes import MultinomialNB as MNB
# from sklearn.cross_validation import cross_val_score
# from sklearn.linear_model import LogisticRegression as LR
# from sklearn.grid_search import GridSearchCV
# import gensim
# import time
# from gensim.models import Word2Vec
# from sklearn.naive_bayes import GaussianNB as GNB


datafile = os.path.join(".", "labeledTrainData.tsv")
# print(datafile)	#.\labeledTrainData.tsv
df = pd.read_csv(datafile, sep="\t", escapechar="\\")


# print("Number of reviews:{}".format(len(df)))
# print(df.head())
# print(df["review"][0])

def display(text, title):
	print(title)
	print("\n------------我是分割线-------------\n")
	print(text)


raw_example = df["review"][0]
# display(raw_example,"示例数据")

example = BeautifulSoup(raw_example, "html.parser").get_text()
# display(example,"去掉html标签")

example_letters = re.sub(r"[^a-zA-Z]", " ", example)
# display(example_letters, "去掉标点符号")

words = example_letters.lower().split()
# display(words,"纯词列表数据")


stopwords=[line.rstrip() for line in open("./stopwords.txt")]
# stopwords={}.fromkeys([line.rstrip() for line in open("./stopwords.txt")])
# print(stopwords)
words_nostop=[w for w in words if w not in stopwords]
# display(words_nostop,"去掉停用词数据")

eng_stopwords=set(stopwords)
def clean_text(text):
	text=BeautifulSoup(text, "html.parser").get_text()
	text=re.sub(r"[^a-zA-Z]", " ", text)
	words=text.lower().split()
	words=[w for w in words if w not in eng_stopwords]
	return " ".join(words)
# cleantext=clean_text(raw_example)
# print(cleantext)

#对每一行使用清洗函数,并保存到新列中
df["clean_review"]=df.review.apply(clean_text)
# print(df.head())

# 抽取bag of words特征(用sklearn的CountVectorizer)
#从中获取总共5000个词作为词典
vectorizer=CountVectorizer(max_features=5000)
train_data_features=vectorizer.fit_transform(df.clean_review).toarray()
# print(train_data_features.shape)	#(25000, 5000)
# print(train_data_features)	#总共5000个词,随机分配到二维数组中

# 训练分类器
forest = RandomForestClassifier(n_estimators=100)
forest=forest.fit(train_data_features,df.sentiment)

confusion=confusion_matrix(df.sentiment,forest.predict(train_data_features))
print(confusion)
#返回结果,甚麽意思?
# [[12500     0]
#  [    0 12500]]

# 删除不用的占内存变量
del df
del train_data_features

datafile = os.path.join(".", "testData.tsv")
df = pd.read_csv(datafile, sep="\t", escapechar="\\")
print("Number of reviews:{}".format(len(df)))
df["clean_review"]=df.review.apply(clean_text)
print(df.head())





