#!/usr/bin/python
# -*- coding:utf-8 -*-


"""
kaggle:https://www.kaggle.com/c/word2vec-nlp-tutorial/data
参考:http://www.cnblogs.com/lijingpeng/p/5787549.html
"""

import os
import pandas as pd
import numpy as np
import re
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer as TFIDF
from sklearn.naive_bayes import MultinomialNB as MNB
from sklearn.cross_validation import cross_val_score
from sklearn.linear_model import LogisticRegression as LR
from sklearn.grid_search import GridSearchCV
import gensim
import nltk
from nltk.corpus import stopwords
import time
from gensim.models import Word2Vec
from sklearn.naive_bayes import GaussianNB as GNB
from sklearn.ensemble import RandomForestClassifier
try:
	import json  # python >= 2.6
except ImportError:
	import simplejson as json  # python <= 2.5
from utils import OtherUtils





# 载入数据集
train = pd.read_csv(os.path.join(".", "sources", "labeledTrainData.tsv"), header=0, delimiter="\t", quoting=3)
test = pd.read_csv(os.path.join(".", "sources","testData.tsv"), header=0, delimiter="\t", quoting=3)

label = train['sentiment']

train_data = OtherUtils.get_deal_data(train["review"])
test_data = OtherUtils.get_deal_data(test["review"])


# # Word2vec
# tokenizer = nltk.data.load(OtherUtils.tokenizer_english)
#
# sentences = OtherUtils.get_sentences_data(train["review"],tokenizer)
#
# 构建word2vec模型
# 模型参数
num_features = 300  # Word vector dimensionality
min_word_count = 40  # Minimum word count
num_workers = 4  # Number of threads to run in parallel
context = 10  # Context window size
downsampling = 1e-3  # Downsample setting for frequent words
# # 训练模型
# print("训练模型中...")
# model = Word2Vec(sentences, workers=num_workers, size=num_features, min_count=min_word_count, window=context,
# 				 sample=downsampling)
# # 保存模型
# print('保存模型...')
# model.init_sims(replace=True)
model_name = os.path.join(".", "wkztarget", "300features_40minwords_10context_True")
# model.save(model_name)


# 从已经训练好的模型中加载使用
model = gensim.models.Word2Vec.load(model_name)

# # 预览模型
# print(model.doesnt_match("man woman child kitchen".split()))
# print(model.doesnt_match("france england germany berlin".split()))
# print(model.doesnt_match("paris berlin london austria".split()))
# print(model.most_similar("man"))
# print(model.most_similar("queen"))
# print(model.most_similar("awful"))
# print(model)








# 使用Word2vec特征
def makeFeatureVec(words, model, num_features):
	'''
	对段落中的所有词向量进行取平均操作
	'''
	featureVec = np.zeros((num_features,), dtype="float32")
	nwords = 0.
	# 这里是在wvIndex2word包含了词表中的所有词，为了检索速度，保存到set中
	index2word_set = set(model.wv.index2word)
	for word in words:
		if word in index2word_set:
			nwords = nwords + 1.
			featureVec = np.add(featureVec, model[word])
	# 取平均
	featureVec = np.divide(featureVec, nwords)
	return featureVec


def getAvgFeatureVecs(reviews, model, num_features):
	'''
	给定一个文本列表，每个文本由一个词列表组成，返回每个文本的词向量平均值
	'''
	counter = 0.
	reviewFeatureVecs = np.zeros((len(reviews), num_features), dtype="float32")
	for review in reviews:
		if counter % 5000. == 0.:
			print("Review %d of %d" % (counter, len(reviews)))
		reviewFeatureVecs[counter] = makeFeatureVec(review, model, num_features)
		counter = counter + 1.
	return reviewFeatureVecs


trainDataVecs = getAvgFeatureVecs(train_data, model, num_features)
testDataVecs = getAvgFeatureVecs(test_data, model, num_features)
print(trainDataVecs)
print(testDataVecs)


# 高斯贝叶斯+Word2vec训练
model_GNB = GNB()
model_GNB.fit(trainDataVecs, label)
print("高斯贝叶斯分类器10折交叉验证得分: ", np.mean(cross_val_score(model_GNB, trainDataVecs, label, cv=10, scoring='roc_auc')))
result = model_GNB.predict(testDataVecs)
output = pd.DataFrame(data={"id": test["id"], "sentiment": result})
output.to_csv("gnb_word2vec.csv", index=False, quoting=3)


# 随机森林+Word2vec训练
forest = RandomForestClassifier(n_estimators=100, n_jobs=2)
print("Fitting a random forest to labeled training data...")
forest.fit(trainDataVecs, label)#这里返回的是同一个对象
print("随机森林分类器10折交叉验证得分: ", np.mean(cross_val_score(forest, trainDataVecs, label, cv=10, scoring='roc_auc')))
# 测试集
result = forest.predict(testDataVecs)
output = pd.DataFrame(data={"id": test["id"], "sentiment": result})
output.to_csv("rf_word2vec.csv", index=False, quoting=3)
