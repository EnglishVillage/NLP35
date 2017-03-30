#! /usr/bin/python
# -*- coding:utf-8 -*-

import os
import re
import numpy as np
import pandas as pd
# 解析网页
from bs4 import BeautifulSoup

import nltk.data
from nltk.corpus import stopwords

from gensim.models import Word2Vec

def load_dataset(name,nrows=None):
	datasets={"unlabeled_train":"unlabeledTrainData.tsv","labeled_train":"labeledTrainData.tsv","test":"testData.tsv"}
	if name not in datasets:
		raise ValueError(name)
	data_file=os.path.join(".","sources",datasets[name])
	df = pd.read_csv(data_file, sep="\t", escapechar="\\", nrows=nrows)
	print("Number of reviews:{}".format(len(df)))
	return df

df=load_dataset("unlabeled_train")
# print(df.head())

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

tokenizer=nltk.data.load("tokenizers/punkt/english.pickle")

def print_call_counts(f):
	n=0
	def wrapped(*args,**kwargs):
		nonlocal n
		n+=1
		if n%1000==1:
			print("method {} called {} times".format(f.__name__,n))
		return f(*args,*kwargs)
	return wrapped

@print_call_counts
def split_sentences(review):
	raw_sentences=tokenizer.tokenize(review.strip())
	sentences=[clean_text(s) for s in raw_sentences if s]
	return sentences

sentences=sum(df.review.apple(split_sentences),[])
print("{} reviews -> {} sentences".format(len(df),len(sentences)))