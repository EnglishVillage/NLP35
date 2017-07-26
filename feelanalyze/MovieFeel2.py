#! /usr/bin/python
# -*- coding:utf-8 -*-

import os, sys, re, time

sys.path.append('/home/esuser/NLP35')
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
import pickle

# 导入自定义的包
from utils import OtherUtils

# from sklearn.naive_bayes import MultinomialNB as MNB
# from sklearn.cross_validation import cross_val_score
# from sklearn.linear_model import LogisticRegression as LR
# from sklearn.grid_search import GridSearchCV
# import gensim
# from gensim.models import Word2Vec
# from sklearn.naive_bayes import GaussianNB as GNB

print("start")

datafile = os.path.join("..", "sources", "labeledTrainData.tsv")
# df = pd.read_csv(datafile, header=0, delimiter="\t", quoting=3)
df = pd.read_csv(datafile, sep="\t", escapechar="\\")
# print(datafile)	#.\labeledTrainData.tsv


# print("Number of reviews:{}".format(len(df)))
print(df.head())


# print(df["review"][0])

def display(text, title):
	print(title)
	print("\n------------我是分割线-------------\n")
	print(text)


# raw_example = df["review"][0]
# display(raw_example,"示例数据")


# cleantext=OtherUtils.review_to_wordlist(raw_example)
# print(cleantext)

# 对每一行使用清洗函数,并保存到新列中
df["clean_review"] = df.review.apply(OtherUtils.review_to_wordlist)
print(df.head())

# 抽取bag of words特征(用sklearn的CountVectorizer)
# 从中获取总共5000个词作为词典
vectorizer = CountVectorizer(max_features=5000)

# train_data_features=vectorizer.fit_transform(df.clean_review).toarray()
# print(train_data_features.shape)	#(25000, 5000)
# print(train_data_features)	#总共5000个词,随机分配到二维数组中

# 训练分类器
# forest = RandomForestClassifier(n_estimators=100)
# forest=forest.fit(train_data_features,df.sentiment)

# 保存模型
forestpkl = os.path.join(".", "wkztarget", "forest.pkl")
# with open(forestpkl, 'wb') as f:
#     pickle.dump(forest, f)



#
# confusion=confusion_matrix(df.sentiment,forest.predict(train_data_features))
# print(confusion)
# 返回结果,甚麽意思?
# 矩阵的每一列表示预测类中的实例，而每行表示实际类中的实例
# [[12500     0]
#  [    0 12500]]

# 删除不用的占内存变量
# del df
# del train_data_features

# datafile = os.path.join(".", "sources", "testData.tsv")
# df = pd.read_csv(datafile, sep="\t", escapechar="\\")
# df["clean_review"] = df.review.apply(OtherUtils.review_to_wordlist)
# # print("Number of reviews:{}".format(len(df)))
# # print(df.head())
#
# # 抽取bag of words特征(用sklearn的CountVectorizer)
# # 从中获取总共5000个词作为词典
# test_data_features = vectorizer.fit_transform(df.clean_review).toarray()
# # print(test_data_features.shape)
#
# # 从文件中读取模型
# forest = pickle.load(open(forestpkl, 'rb'))
# result = forest.predict(test_data_features)
# output = pd.DataFrame({"id": df.id, "sentiment": result})
# # print(output.head())
#
# output.to_csv(os.path.join(".", "wkztarget", "Bag_of_Words_model.csv"), index=False)

# del df
# del train_data_features
