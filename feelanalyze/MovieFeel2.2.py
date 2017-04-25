#! /usr/bin/python
# -*- coding:utf-8 -*-

import os
import re
import numpy as np
import pandas as pd
import logging
# 解析网页
from bs4 import BeautifulSoup
import nltk.data
nltk.download('punkt')
from nltk.corpus import stopwords

from gensim.models import Word2Vec
# 随机森林
from sklearn.ensemble import RandomForestClassifier
# 评估矩阵
from sklearn.metrics import confusion_matrix



def load_dataset(name,nrows=None):
	datasets={"unlabeled_train":"unlabeledTrainData.tsv","labeled_train":"labeledTrainData.tsv","test":"testData.tsv"}
	if name not in datasets:
		raise ValueError(name)
	data_file=os.path.join(".","sources",datasets[name])
	df = pd.read_csv(data_file, sep="\t", escapechar="\\", nrows=nrows)
	print("Number of reviews:{}".format(len(df)))
	return df

eng_stopwords=set(stopwords.words("english"))
def clean_text(text,remover_stopwords=False):
	# 去掉html标签
	text = BeautifulSoup(text, "html.parser").get_text()
	# 去掉标点符号
	text = re.sub(r"[^a-zA-Z]", " ", text)
	# 纯词列表数据
	words = text.lower().split()
	# 去掉停用词数据
	if remover_stopwords:
		words = [w for w in words if w not in eng_stopwords]
	return " ".join(words)

#
# df=load_dataset("unlabeled_train")
# # print(df.head())
#

#
# tokenizer=nltk.data.load("tokenizers/punkt/english.pickle")
#
# def print_call_counts(f):
# 	n=0
# 	def wrapped(*args,**kwargs):
# 		nonlocal n
# 		n+=1
# 		if n%1000==1:
# 			print("method {} called {} times".format(f.__name__,n))
# 		return f(*args,*kwargs)
# 	return wrapped
#
# @print_call_counts
# def split_sentences(review):
# 	raw_sentences=tokenizer.tokenize(review.strip())
# 	sentences=[clean_text(s) for s in raw_sentences if s]
# 	return sentences
#
# sentences=sum(df.review.apply(split_sentences),[])
# print("{} reviews -> {} sentences".format(len(df),len(sentences)))
#
# logging.basicConfig(level=logging.INFO, filename='./wkzlog/info.log',
# 					format='%(asctime)s : %(levelname)s : %(message)s',
# 					datefmt='%Y-%m-%d %H:%M:%S')
#设定词向量训练的参数
num_features=300	#Word vector dimensinality
min_word_count=40	#min word count
num_workers=4		#Number of thrends to run parellel
context=10			#context window size
downsampling=1e-3	#downsample setting for frequent words
model_name="{}features_{}minwords_{}context.model".format(num_features,min_word_count,context)

# print("trainging model...")
# model=Word2Vec(sentences,workers=num_workers,size=num_features,min_count=min_word_count,window=context,sample=downsampling)
# model.init_sims(replace=True)
#
model_path = os.path.join(".", "wkztarget", model_name)
# model.save(model_path)

model = Word2Vec.load(model_path)

print(model.doesnt_match("man woman child kitchen".split()))
print(model.doesnt_match("france england germany berlin".split()))
print(model.most_similar("man"))
print(model.most_similar("queen"))
print(model.most_similar("awful"))

# model = Word2Vec.load(model_path)
df = load_dataset("labeled_train")
print(df.head())

def to_review_vector(review):
	words = clean_text(review, remover_stopwords=True)
	array = np.array([model[w] for w in words if w in model])
	return pd.Series(array.mean(axis=0))


train_data_features = df.review.apply(to_review_vector)
train_data_features.head()

# 用随机森林构建分类器
forest = RandomForestClassifier(n_estimators=100, random_state=42)
forest.fit(train_data_features,df.sentiment)

matrix = confusion_matrix(df.sentiment, forest.predict(train_data_features))
print(matrix)

#
del df
del train_data_features

df=load_dataset("test")
# df.head()

train_data_features = df.review.apply(to_review_vector)
train_data_features.head()

# 用随机森林构建分类器
result = forest.predict(train_data_features)
output = pd.DataFrame({"id": df.id, "sentiment": result})
output.to_csv(os.path.join(".","wkztarget","Word2Vec_model.csv"),index=False)
output.head()

#
del df
del train_data_features
del forest

model.vw.syn0






