#! /usr/bin/python
# -*- coding:utf-8 -*-

import os, sys, re
import numpy as np
import pandas as pd
import logging
# 解析网页
from bs4 import BeautifulSoup
import nltk.data
# nltk.download('punkt')
from nltk.corpus import stopwords
from gensim.models.word2vec import Word2Vec
# 随机森林
from sklearn.ensemble import RandomForestClassifier
# 评估矩阵
from sklearn.metrics import confusion_matrix
# Kmeans聚类
from sklearn.cluster import KMeans
# 评估model效果
from sklearn.cross_validation import train_test_split
# 将对象/模型转化为二进制
from sklearn.externals import joblib
# SVC是SVM的一种Type，是用来的做分类的，SVR是SVM的另一种Type，是用来的做回归的。
from sklearn.svm import SVC
import jieba

try:
	# 序列化
	import cPickle as pickle
except ImportError:
	import pickle


def load_dataset(name, nrows=None):
	datasets = {"unlabeled_train": "unlabeledTrainData.tsv", "labeled_train": "labeledTrainData.tsv", "test": "testData.tsv"}
	if name not in datasets:
		raise ValueError(name)
	data_file = os.path.join("..", "sources", datasets[name])
	df = pd.read_csv(data_file, sep="\t", escapechar="\\", nrows=nrows)
	print("Number of reviews:{}".format(len(df)))
	return df


eng_stopwords = set(stopwords.words("english"))


def clean_text(text, remover_stopwords=False):
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
# 设定词向量训练的参数
num_features = 300  # Word vector dimensinality
min_word_count = 40  # min word count
num_workers = 4  # Number of thrends to run parellel
context = 10  # context window size
downsampling = 1e-3  # downsample setting for frequent words
model_name = "{}features_{}minwords_{}context".format(num_features, min_word_count, context)
model_path = os.path.join("..", "wkztarget", model_name)

# print("trainging model...")
# model=Word2Vec(sentences,workers=num_workers,size=num_features,min_count=min_word_count,window=context,sample=downsampling)
# model.init_sims(replace=True)
#
# model.save(model_path)

# 加载Word2Vec模型
model = Word2Vec.load(model_path)

# print(model.doesnt_match("man woman child kitchen".split()))
# print(model.doesnt_match("france england germany berlin".split()))
# print(model.most_similar("man"))
# print(model.most_similar("queen"))
# print(model.most_similar("awful"))

# df = load_dataset("labeled_train")
# print(df.head())


# def to_review_vector(review):
# 	words = clean_text(review, remover_stopwords=True)
# 	array = np.array([model[w] for w in words if w in model])
# 	return pd.Series(array.mean(axis=0))
#
#
# train_data_features = df.review.apply(to_review_vector)
# train_data_features.head()
#
# # 用随机森林构建分类器
# forest = RandomForestClassifier(n_estimators=100, random_state=42)
# forest.fit(train_data_features, df.sentiment)
#
# matrix = confusion_matrix(df.sentiment, forest.predict(train_data_features))
# print(matrix)
#
# #
# del df
# del train_data_features
#
# df = load_dataset("test")
# # df.head()
#
# train_data_features = df.review.apply(to_review_vector)
# train_data_features.head()
#
# # 用随机森林构建分类器
# result = forest.predict(train_data_features)
# output = pd.DataFrame({"id": df.id, "sentiment": result})
# output.to_csv(os.path.join("..", "wkztarget", "Word2Vec_model.csv"), index=False)
# output.head()
#
# #
# del df
# del train_data_features
# del forest

word_vectors = model.wv.syn0
num_clusters = word_vectors.shape[0]

if __name__ == '__main__':
	k_means_clustering = KMeans(n_clusters=num_clusters, n_jobs=4)
	# idx = k_means_clustering.fit_predict(word_vectors)
	k_means_clustering.fit(word_vectors)
	# pkl = os.path.join(".", "wkztarget", "KMeans.pkl")
	# with open(pkl, 'wb') as f:
	#     pickle.dump(k_means_clustering, f)
	# idx=k_means_clustering.labels_


	# word_centroid_map = dict(zip(model.index2word, idx))
	#
	# with open(os.path.join("..", "wkztarget", "word_centroid_map_10avg.pickle"), "bw") as f:
	# 	pickle.dump(word_centroid_map, f)
	# # with open(os.path.join("..", "wkztarget", "word_centroid_map_10avg.pickle"), "br") as f:
	# # 	word_centroid_map=pickle.load(f)
	#
	# for cluster in range(0,10):
	# 	print("\nCluster %d" %cluster)
	# 	print([w for w,c in word_centroid_map.items() if c==cluster])
	#
	# wordset	=set(word_centroid_map.keys())
	# def make_cluster_bag(review):
	# 	words=clean_text(review,remover_stopwords=True)
	# 	return(pd.Series([word_centroid_map[w] for w in words if w in wordset]).value_counts().reindex(range(num_clusters+1),fill_value=0))
	#
	# df=load_dataset("labeled_train")
	print(1)

#############################################################################################


# 载入数据,做预处理(分词),切分训练集与测试集
def load_file_and_preprocessing():
	neg = pd.read_excel(os.path.join("..", "sources", "neg.xls"), header=None, index=None)
	pos = pd.read_excel(os.path.join("..", "sources", "neg.xls"), header=None, index=None)
	cw = lambda x: jieba.lcut(x)
	neg["words"] = neg[0].apply(cw)
	pos["words"] = pos[0].apply(cw)

	# print pos["words"]
	# use 1 for positive sentiment,0 for negative
	y = np.concatenate((np.ones(len(pos)), np.zeros(len(neg))))
	x_train, x_test, y_train, y_test = train_test_split(np.concatenate((pos["words"]), (neg["words"])))
	np.save(os.path.join("..", "wkztarget", "svm_data", "y_train.npy"), y_train)
	np.save(os.path.join("..", "wkztarget", "svm_data", "y_test.npy"), y_test)
	return x_train, x_test


# 对每个句子的所有词向量取均值,来生成一个句子的vector
def build_sentence_vector(text, size, imdb_w2v):
	vec = np.zeros(size).reshape((1, size))
	count = 0
	for word in text:
		try:
			vec += imdb_w2v[word].reshape((1, size))
			count += 1.
		except KeyError:
			continue
	if count != 0:
		vec /= count
	return vec


# 计算词向量
def get_train_vecs(x_train, x_test):
	n_dim = 300
	# 初始化模型和词表
	imdb_w2v = Word2Vec(size=n_dim, min_count=10)
	imdb_w2v.build_vocab(x_train)
	# 在评论训练集上建模(可能会花费几分钟)
	imdb_w2v.train(x_train)


# train_vecs=np.concatenate([build_sentence_vector(z,n_dim,imdb_w2v) for z in ])
# # train_vecs=scale(train_vecs)
# np.save(os.path.join("..", "wkztarget", "svm_data", "train_vecs.npy"),train_vecs)
# print(train_vecs.shape)
# # 在测试集上训练
# imdb_w2v.train(x_test)
# imdb_w2v.save(os.path.join("..", "wkztarget", "svm_data","w2v_model", "w2v_model.pkl"))
# #Build test tweet vectors then scale
# test_vecs=np.concatenate([build_sentence_vector(z,n_dim,imdb_w2v) for z in ])
# # test_vecs=scale(test_vecs)
# np.save(os.path.join("..", "wkztarget", "svm_data", "test_vecs.npy"),test_vecs)
# print(test_vecs.shape)

def get_data():
	train_vecs = np.load(os.path.join("..", "wkztarget", "svm_data", "train_vecs.npy"))
	y_train = np.load(os.path.join("..", "wkztarget", "svm_data", "y_train.npy"))
	test_vecs = np.load(os.path.join("..", "wkztarget", "svm_data", "test_vecs.npy"))
	y_test = np.load(os.path.join("..", "wkztarget", "svm_data", "y_test.npy"))
	return train_vecs, y_train, test_vecs, y_test


# 训练SVM模型
def svm_train(train_vecs, y_train, test_vecs, y_test):
	clf = SVC(kernel="rbf", verbose=True)
	clf.fit(train_vecs, y_train)
	joblib.dump(clf, os.path.join("..", "wkztarget", "svm_data", "svm_model", "model.pkl"))
	print(clf.score(test_vecs, y_test))


# 构建待预测句子的向量
def get_predict_vecs(words):
	n_dim = 300
	imdb_w2v = Word2Vec.load(os.path.join("..", "wkztarget", "svm_data", "w2v_model", "w2v_model.pkl"))
	# imdb_w2v.train(words)
	train_vecs = build_sentence_vector(words, n_dim, imdb_w2v)
	# print(train_vecs.shape)
	return train_vecs


# 对单个句子进行情感判断
def svm_predict(string):
	words = jieba.lcut(string)
	words_vecs = get_predict_vecs(words)
	clf = joblib.load(os.path.join("..", "wkztarget", "svm_data", "svm_model", "model.pkl"))
	result = clf.predict(words_vecs)
	if int(result[0]) == 1:
		print(string, " positive")
	else:
		print(string, " negative")


string = "电池充塞了电连手机都打不开.简直烂的要命.真是金玉其外,几絮其中!连5号电池都"
# string ="牛逼的手机,从3米高的地方摔下去都没坏,质量非常好"
# svm_predict(string)
