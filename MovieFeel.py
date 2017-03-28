#!/usr/bin/python
# -*- coding:utf-8 -*-

"""
参考:
http://www.cnblogs.com/lijingpeng/p/5787549.html
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


# 载入数据集
train = pd.read_csv(os.path.join("./sources","labeledTrainData.tsv"), header=0, delimiter="\t", quoting=3)
test = pd.read_csv(os.path.join("./sources","testData.tsv"), header=0, delimiter="\t", quoting=3)
print(train.head(1))
print(test.head(1))


# 预处理数据，得到单词数组【去HTML标签，去掉非字母字符】
def review_to_wordlist(review):
	'''
	把IMDB的评论转成词序列
	参考：http://blog.csdn.net/longxinchen_ml/article/details/50629613
	'''
	# 去掉HTML标签，拿到内容
	review_text = BeautifulSoup(review, "html.parser").get_text()
	# 用正则表达式取出符合规范的部分
	review_text = re.sub("[^a-zA-Z]", " ", review_text)
	# 小写化所有的词，并转成词list
	words = review_text.lower().split()
	# 返回words
	return words


# 预处理数据
label = train['sentiment']
train_data = []
for i in range(len(train['review'])):
	train_data.append(' '.join(review_to_wordlist(train['review'][i])))
test_data = []
for i in range(len(test['review'])):
	test_data.append(' '.join(review_to_wordlist(test['review'][i])))
# 预览数据
print(train_data[0], '\n')
print(test_data[0])



# 特征处理【用于朴素贝叶斯和逻辑回归】
# 参考：http://blog.csdn.net/longxinchen_ml/article/details/50629613
tfidf = TFIDF(min_df=2,  # 最小支持度为2
			  max_features=None,
			  strip_accents='unicode',
			  analyzer='word',
			  token_pattern=r'\w{1,}',
			  ngram_range=(1, 3),  # 二元文法模型
			  use_idf=1,
			  smooth_idf=1,
			  sublinear_tf=1,
			  stop_words='english')  # 去掉英文停用词
# 合并训练和测试集以便进行TFIDF向量化操作
data_all = train_data + test_data
len_train = len(train_data)
tfidf.fit(data_all)
data_all = tfidf.transform(data_all)
# 恢复成训练集和测试集部分
train_x = data_all[:len_train]
test_x = data_all[len_train:]
print('TF-IDF处理结束.')



# 1.朴素贝叶斯训练
model_NB = MNB()
model_NB.fit(train_x, label)
MNB(alpha=1.0, class_prior=None, fit_prior=True)
print("多项式贝叶斯分类器10折交叉验证得分: ", np.mean(cross_val_score(model_NB, train_x, label, cv=10, scoring='roc_auc')))
test_predicted = np.array(model_NB.predict(test_x))
print('保存结果...')
nb_output = pd.DataFrame(data=test_predicted, columns=['sentiment'])
nb_output['id'] = test['id']
nb_output = nb_output[['id', 'sentiment']]
# nb_output.to_csv('nb_output.csv', index=False)
print('结束.')





# # 2.逻辑回归
# # 设定grid search的参数
# grid_values = {'C':[30]}
# # 设定打分为roc_auc
# model_LR = GridSearchCV(LR(penalty = 'l2', dual = True, random_state = 0), grid_values, scoring = 'roc_auc', cv = 20)
# model_LR.fit(train_x, label)
# # 20折交叉验证
# GridSearchCV(cv=20, estimator=LR(C=1.0, class_weight=None, dual=True,
#              fit_intercept=True, intercept_scaling=1, penalty='l2', random_state=0, tol=0.0001),
#         fit_params={}, iid=True, n_jobs=1,
#         param_grid={'C': [30]}, pre_dispatch='2*n_jobs', refit=True,
#         scoring='roc_auc', verbose=0)
# #输出结果
# print (model_LR.grid_scores_)
#
# test_predicted = np.array(model_LR.predict(test_x))
# print('保存结果...')
# lr_output = pd.DataFrame(data=test_predicted, columns=['sentiment'])
# lr_output['id'] = test['id']
# lr_output = lr_output[['id', 'sentiment']]
# lr_output.to_csv('lr_output.csv', index=False)
# print('结束.')




# # Word2vec
# tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
#
# def review_to_wordlist(review, remove_stopwords=False):
# 	review_text = BeautifulSoup(review, "html.parser").get_text()
# 	review_text = re.sub("[^a-zA-Z]", " ", review_text)
# 	words = review_text.lower().split()
# 	if remove_stopwords:
# 		stops = set(stopwords.words("english"))
# 		words = [w for w in words if not w in stops]
# 	return (words)
#
# def review_to_sentences(review, tokenizer, remove_stopwords=False):
# 	'''
# 	将评论段落转换为句子，返回句子列表，每个句子由一堆词组成
# 	'''
# 	# raw_sentences = tokenizer.tokenize(review.strip().decode('utf8'))
# 	raw_sentences = tokenizer.tokenize(review.strip())
#
# 	sentences = []
# 	for raw_sentence in raw_sentences:
# 		if len(raw_sentence) > 0:
# 			# 获取句子中的词列表
# 			sentences.append(review_to_wordlist(raw_sentence, remove_stopwords))
# 	return sentences
#
# sentences = []
# for i, review in enumerate(train["review"]):
# 	sentences += review_to_sentences(review, tokenizer)
#
unlabeled_train = pd.read_csv(os.path.join("./sources","unlabeledTrainData.tsv"), header=0, delimiter="\t", quoting=3)
# for review in unlabeled_train["review"]:
# 	sentences += review_to_sentences(review, tokenizer)
# print('预处理unlabeled_train data...')
# print(len(train_data))
# print(len(sentences))




# # 构建word2vec模型
# # 模型参数
num_features = 300  # Word vector dimensionality
# min_word_count = 40  # Minimum word count
# num_workers = 4  # Number of threads to run in parallel
# context = 10  # Context window size
# downsampling = 1e-3  # Downsample setting for frequent words
# # 训练模型
# print("训练模型中...")
# model = Word2Vec(sentences, workers=num_workers, \
# 				 size=num_features, min_count=min_word_count, \
# 				 window=context, sample=downsampling)
# print('保存模型...')
# model.init_sims(replace=True)
# model_name = "300features_40minwords_10context"
# model.save(model_name)

# 从已经训练好的模型中加载使用
# model = gensim.models.Word2Vec.load(os.path.join("./target","300features_40minwords_10context"))


# 预览模型
# print(model.doesnt_match("man woman child kitchen".split()))
# print(model.doesnt_match("france england germany berlin".split()))
# print(model.doesnt_match("paris berlin london austria".split()))
# print(model.most_similar("man"))
# print(model.most_similar("queen"))
# print(model.most_similar("awful"))


# # 使用Word2vec特征
# def makeFeatureVec(words, model, num_features):
# 	'''
# 	对段落中的所有词向量进行取平均操作
# 	'''
# 	featureVec = np.zeros((num_features,), dtype="float32")
# 	nwords = 0.
# 	# 这里是在wvIndex2word包含了词表中的所有词，为了检索速度，保存到set中
# 	index2word_set = set(model.wv.index2word)
# 	for word in words:
# 		if word in index2word_set:
# 			nwords = nwords + 1.
# 			featureVec = np.add(featureVec, model[word])
# 	# 取平均
# 	featureVec = np.divide(featureVec, nwords)
# 	return featureVec
#
#
# def getAvgFeatureVecs(reviews, model, num_features):
# 	'''
# 	给定一个文本列表，每个文本由一个词列表组成，返回每个文本的词向量平均值
# 	'''
# 	counter = 0.
# 	reviewFeatureVecs = np.zeros((len(reviews), num_features), dtype="float32")
# 	for review in reviews:
# 		if counter % 5000. == 0.:
# 			print("Review %d of %d" % (counter, len(reviews)))
# 		reviewFeatureVecs[counter] = makeFeatureVec(review, model, num_features)
# 		counter = counter + 1.
# 	return reviewFeatureVecs
#
#
# trainDataVecs = getAvgFeatureVecs(train_data, model, num_features)
# # print(trainDataVecs)
# testDataVecs = getAvgFeatureVecs(test_data, model, num_features)
# # print(testDataVecs)



# # 高斯贝叶斯+Word2vec训练
# model_GNB = GNB()
# GNBfit = model_GNB.fit(trainDataVecs, label)
# print("高斯贝叶斯分类器10折交叉验证得分: ", np.mean(cross_val_score(model_GNB, trainDataVecs, label, cv=10, scoring='roc_auc')))
# result = GNBfit.predict(testDataVecs)
# output = pd.DataFrame(data={"id": test["id"], "sentiment": result})
# output.to_csv("gnb_word2vec.csv", index=False, quoting=3)


# # 随机森林+Word2vec训练
# forest = RandomForestClassifier(n_estimators=100, n_jobs=2)
# print("Fitting a random forest to labeled training data...")
# forestfit = forest.fit(trainDataVecs, label)
# print("随机森林分类器10折交叉验证得分: ", np.mean(cross_val_score(forest, trainDataVecs, label, cv=10, scoring='roc_auc')))
# # 测试集
# result = forestfit.predict(testDataVecs)
# output = pd.DataFrame(data={"id": test["id"], "sentiment": result})
# output.to_csv("rf_word2vec.csv", index=False, quoting=3)
