#!/usr/bin/python
# -*- coding:utf-8 -*-

"""
参考:
http://www.cnblogs.com/lijingpeng/p/5787549.html
"""

import pandas as pd
import numpy as np
import re
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer as TFIDF
from sklearn.naive_bayes import MultinomialNB as MNB
from sklearn.cross_validation import cross_val_score

wkzpath = "D:/MyDocument/MyWork/ML/ChinaHandoopML/Sources/NLP35/"




# 载入数据集
train = pd.read_csv(wkzpath + 'labeledTrainData.tsv', header=0, delimiter="\t", quoting=3)
test = pd.read_csv(wkzpath + 'testData.tsv', header=0, delimiter="\t", quoting=3)
print(train.head(1))
print(test.head(1))


# 预处理数据
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

# 特征处理
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


# 朴素贝叶斯训练
model_NB = MNB()
model_NB.fit(train_x, label)
MNB(alpha=1.0, class_prior=None, fit_prior=True)
print("多项式贝叶斯分类器10折交叉验证得分: ", np.mean(cross_val_score(model_NB, train_x, label, cv=10, scoring='roc_auc')))


test_predicted = np.array(model_NB.predict(test_x))
print('保存结果...')
nb_output = pd.DataFrame(data=test_predicted, columns=['sentiment'])
nb_output['id'] = test['id']
nb_output = nb_output[['id', 'sentiment']]
nb_output.to_csv('nb_output.csv', index=False)
print('结束.')



