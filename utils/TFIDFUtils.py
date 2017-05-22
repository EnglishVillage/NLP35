#!/usr/bin/python
# -*- coding:utf-8 -*-

import os, sys, re, time
from sklearn.feature_extraction.text import TfidfVectorizer as TFIDF
from utils import OtherUtils


def get_transform_data(model_name, data):
	tmpfile = OtherUtils.get_target_path(model_name)
	# 判断文件是否存在
	if os.path.exists(tmpfile):
		tfidf = OtherUtils.load_fit_model(model_name)
	else:
		# 特征处理【用于朴素贝叶斯和逻辑回归】
		# 参考：http://blog.csdn.net/longxinchen_ml/article/details/50629613
		tfidf = TFIDF(min_df=2,  # 最小支持度为2
					  max_features=None, strip_accents='unicode', analyzer='word', token_pattern=r'\w{1,}',
					  ngram_range=(1, 3),  # 二元文法模型
					  use_idf=1, smooth_idf=1,  # 平滑idf的参数可设置大于0的数,use_idf设置为True才有效.
					  sublinear_tf=1, stop_words='english')  # 去掉英文停用词
		# 训练并保存模型
		tfidf.fit(data)
		OtherUtils.save_fit_model(model_name, tfidf)
	# 恢复成训练集和测试集部分
	return tfidf,tfidf.transform(data)
