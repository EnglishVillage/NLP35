#!/usr/bin/python
# -*- coding:utf-8 -*-


"""

这个任务主要是对电影评论文本进行情感分类，主要分为正面评论和负面评论，所以是一个二分类问题，二分类模型我们可以选取一些常见的模型比如贝叶斯、逻辑回归等，
这里挑战之一是文本内容的向量化，因此，我们首先尝试基于TF-IDF的向量化方法，然后尝试word2vec。

kaggle:https://www.kaggle.com/c/word2vec-nlp-tutorial/data
参考:http://www.cnblogs.com/lijingpeng/p/5787549.html
"""


import os, sys, re, time
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer as TFIDF
from sklearn.naive_bayes import MultinomialNB as MNB
from sklearn.cross_validation import cross_val_score
from sklearn.linear_model import LogisticRegression as LR
from sklearn.grid_search import GridSearchCV
import gensim
import nltk
from nltk.corpus import stopwords
import pickle
from gensim.models import Word2Vec
from sklearn.naive_bayes import GaussianNB as GNB
from sklearn.ensemble import RandomForestClassifier
try:
	import json  # python >= 2.6
except ImportError:
	import simplejson as json  # python <= 2.5

# 导入自定义的包
sys.path.append(os.path.join("..", "utils"))

from utils import TFIDFUtils,OtherUtils




# 载入数据集
train = pd.read_csv(os.path.join("..", "sources", "labeledTrainData.tsv"), header=0, delimiter="\t", quoting=3)
test = pd.read_csv(os.path.join("..", "sources","testData.tsv"), header=0, delimiter="\t", quoting=3)

label = train['sentiment']

train_data = OtherUtils.get_deal_data(train["review"])
test_data = OtherUtils.get_deal_data(test["review"])


# # 合并训练和测试集以便进行TFIDF向量化操作
data_all = train_data + test_data
tfidf,data_all =TFIDFUtils.get_transform_data("tfidf.pkl",data_all)
# print(tfidf.get_feature_names()[:20])		#获取所有特征值
# print(data_all[:20].toarray())			#获取特征值所对应的向量(该特征值不存在,在index处不存在用0表示)

len_train = len(train_data)
train_x = data_all[:len_train]
# test_x = data_all[len_train:]
# print('TF-IDF处理结束.')



# # 1.朴素贝叶斯训练
# model_NB = MNB()
# model_NB.fit(train_x, label)
# # 保存模型
# model_name="MNB.pkl"
# OtherUtils.save_fit_model(model_name, model_NB)
model_name="MNB.pkl"
model_NB=OtherUtils.load_fit_model(model_name)

MNB(alpha=1.0, class_prior=None, fit_prior=True)
print("多项式贝叶斯分类器10折交叉验证得分: ", np.mean(cross_val_score(model_NB, train_x, label, cv=10, scoring='roc_auc')))

# 1. 提交最终的结果到kaggle，AUC为：0.85728，排名300左右，50%的水平
# 2. ngram_range = 3, 三元文法，AUC为0.85924

# test_predicted = np.array(model_NB.predict(test_x))
# print('保存结果...')
# nb_output = pd.DataFrame(data=test_predicted, columns=['sentiment'])
# nb_output['id'] = test['id']
# nb_output = nb_output[['id', 'sentiment']]
# nb_output.to_csv('nb_output.csv', index=False)
# print('结束.')




# 2.逻辑回归
# 设定grid search的参数
# grid_values = {'C':[30]}
# # 设定打分为roc_auc
# model_LR = GridSearchCV(LR(penalty = 'l2', dual = True, random_state = 0), grid_values, scoring = 'roc_auc', cv = 20)
# model_LR.fit(train_x, label)
# # 保存模型
# model_name="lr.pkl"
# OtherUtils.save_fit_model(model_name, model_LR)

# model_name="lr.pkl"
# model_LR=OtherUtils.load_fit_model(model_name)
#
# # 20折交叉验证
# lr = LR(C=1.0, class_weight=None, dual=True, fit_intercept=True, intercept_scaling=1, penalty='l2', random_state=0, tol=0.0001)
# GridSearchCV(cv=20, estimator=lr,
#         fit_params={}, iid=True, n_jobs=1,
#         param_grid={'C': [30]}, pre_dispatch='2*n_jobs', refit=True,
#         scoring='roc_auc', verbose=0)
# #输出结果
# print (model_LR.grid_scores_)

# 1. 提交最终的结果到kaggle，AUC为：0.88956，排名260左右，比之前贝叶斯模型有所提高
# 2. 三元文法，AUC为0.89076

# test_predicted = np.array(model_LR.predict(test_x))
# print('保存结果...')
# lr_output = pd.DataFrame(data=test_predicted, columns=['sentiment'])
# lr_output['id'] = test['id']
# lr_output = lr_output[['id', 'sentiment']]
# lr_output.to_csv('lr_output.csv', index=False)
# print('结束.')
