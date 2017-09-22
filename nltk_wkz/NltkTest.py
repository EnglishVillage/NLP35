#! /usr/bin/python3.5
# -*- coding:utf-8 -*-

import os, sys, re, time

from utils import IOUtils

sys.path.append('/home/esuser/NLP35')

import jieba
import nltk
from nltk.corpus import brown  # 语料库
from nltk.corpus import stopwords  # 停止词
from nltk.tokenize import word_tokenize  # 分词
from nltk.stem.porter import PorterStemmer  # Stemming 词干提取
from nltk.stem.lancaster import LancasterStemmer  # Stemming 词干提取
from nltk.stem import SnowballStemmer  # Stemming 词干提取
from nltk.stem.porter import PorterStemmer  # Stemming 词干提取
from nltk.stem import WordNetLemmatizer  # Lemmatization 词形归一
from nltk.classify import NaiveBayesClassifier

"""NLTK自带语料库"""
# print(brown.categories())
# # ['adventure', 'belles_lettres', 'editorial', 'fiction', 'government', 'hobbies', 'humor', 'learned', 'lore', 'mystery', 'news', 'religion', 'reviews', 'romance', 'science_fiction']
# print(len(brown.sents()))
# print(len(brown.words()))

"""英文分词"""
# sentence = "hello, world"
# tokens = word_tokenize(sentence)
# print(tokens)

"""中文分词"""
# 全模式
# seg_list = jieba.cut("我来到北京清华大学", cut_all=True)
# print("Full Mode:", "/ ".join(seg_list))
# 北京/ 清华/ 清华大学/ 华大/ 大学

# 精确模式
# seg_list = jieba.cut("我来到北京清华大学", cut_all=False)
# print("Default Mode:", "/ ".join(seg_list))
#  北京/ 清华大学

# 默认是精确模式
# seg_list = jieba.cut("他来到了网易杭研大厦")
# print(", ".join(seg_list))

# 搜索引擎模式
# seg_list = jieba.cut_for_search("小明硕士毕业于中国科学院计算所，后在日本京都大学深造")
# print(", ".join(seg_list))
# 中国, 科学, 学院, 科学院, 中国科学院, 计算, 计算所

"""社交网络语言的tokenize"""
# 未优化
# tweet = 'RT @angelababy: love you baby! :D http://ah.love #168cm'
# print(word_tokenize(tweet))

# 优化後
# emoticons_str = r"""
#  (?:
#  [:=;] # 眼睛
#  [oO\-]? # 鼻子
#  [D\)\]\(\]/\\OpP] # 嘴
#  )"""
# regex_str = [
# 	emoticons_str,
# 	r'<[^>]+>',  # HTML tags
# 	r'(?:@[\w_]+)',  # @某人
# 	r"(?:\#+[\w_]+[\w\'_\-]*[\w_]+)",  # 话题标签
# 	r'http[s]?://(?:[a-z]|[0-9]|[$-_@.&amp;+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+',  # URLs
# 	r'(?:(?:\d+,?)+(?:\.?\d+)?)',  # 数字
# 	r"(?:[a-z][a-z'\-_]+[a-z])",  # 含有 - 和 ' 的单词
# 	r'(?:[\w_]+)',  # 其他
# 	r'(?:\S)'  # 其他
# ]
# # re.VERBOSE忽略注释及没用空格
# tokens_re = re.compile(r'(' + '|'.join(regex_str) + ')', re.VERBOSE | re.IGNORECASE)
# emoticon_re = re.compile(r'^' + emoticons_str + '$', re.VERBOSE | re.IGNORECASE)
# def tokenize(s): return tokens_re.findall(s)
# def preprocess(s, lowercase=False):
# 	tokens = tokenize(s)
# 	if lowercase:
# 		tokens = [token if emoticon_re.search(token) else token.lower() for token in tokens]
# 	return tokens

# tweet = 'RT @angelababy: love you baby! :D http://ah.love #168cm'
# print(preprocess(tweet))

"""Stemming 词干提取：一般来说，就是把不影响词性的inflection的小尾巴砍掉"""
# porter_stemmer = PorterStemmer()
# print(porter_stemmer.stem('maximum'))
# print(porter_stemmer.stem('presumably'))
# print(porter_stemmer.stem('multiply'))
# print(porter_stemmer.stem('provision'))
# # maximum
# # presum
# # multipli
# # provis
# lancaster_stemmer = LancasterStemmer()
# print(lancaster_stemmer.stem('maximum'))
# print(lancaster_stemmer.stem('presumably'))
# print(lancaster_stemmer.stem('multiply'))
# print(lancaster_stemmer.stem('provision'))
# # maxim
# # presum
# # multiply
# # provid
# snowball_stemmer = SnowballStemmer('english')
# print(snowball_stemmer.stem('maximum'))
# print(snowball_stemmer.stem('presumably'))
# print(snowball_stemmer.stem('multiply'))
# print(snowball_stemmer.stem('provision'))
# # maximum
# # presum
# # multipli
# # provis
# p = PorterStemmer()
# print(p.stem('went'))
# print(p.stem('wenting'))

"""Lemmatization 词形归一：把各种类型的词的变形，都归为一个形式"""
# wordnet_lemmatizer = WordNetLemmatizer()
# print(wordnet_lemmatizer.lemmatize('dogs'))
# print(wordnet_lemmatizer.lemmatize('churches'))
# print(wordnet_lemmatizer.lemmatize('aardwolves'))
# print(wordnet_lemmatizer.lemmatize('abaci'))
# print(wordnet_lemmatizer.lemmatize('hardrock'))

# NLTK更好地实现Lemma
# # 木有POS Tag(Part-of-speech tagging词性标注)，默认是NN 名词
# print(wordnet_lemmatizer.lemmatize('are'))
# print(wordnet_lemmatizer.lemmatize('is'))
# # 加上POS Tag
# print(wordnet_lemmatizer.lemmatize('is', pos='v'))
# print(wordnet_lemmatizer.lemmatize('are', pos ='v'))


"""NLTK标注POS Tag"""
# text = word_tokenize('what does the fox say')
# print(nltk.pos_tag(text))
# # [('what', 'WDT'), ('does', 'VBZ'), ('the', 'DT'), ('fox', 'NNS'), ('say', 'VBP')]

"""停止词Stopwords"""
# word_list = ["we", "are", "the", "world"]
# filtered_words = [word for word in word_list if word not in stopwords.words('english')]
# print(filtered_words)

"""NLTK完成简单的情感分析"""
# # 写的多,一眼望穿
# sentiment_dictionary = {}
# with open(IOUtils.get_path_sources('AFINN-111.txt')) as file:
# 	for line in file:
# 		word, score = line.split('\t')
# 		sentiment_dictionary[word] = int(score)
# # 一行代码
# with open(IOUtils.get_path_sources('AFINN-111.txt')) as file:
# 	sentiment_dictionary = dict(map(lambda k: (k[0],int(k[1])), [(line.split('\t')) for line in file]))
# # print(len(sentiment_dictionary))
#
# 跑一遍整个句子，把对应的值相加. 有值就是Dict中的值，没有就是0
# words="i like the world i do not like people".split()
# total_score = sum(sentiment_dictionary.get(word, 0) for word in words)
# print(total_score)

"""配上ML的情感分析(应用：文本相似度)"""
# 随手造点训练集
s1 = 'this is a good book'
s2 = 'this is a awesome book'
s3 = 'this is a bad book'
s4 = 'this is a terrible book'
def preprocess(s):
	# Func: 句子处理
	# 这里简单的用了split(), 把句子中每个单词分开
	# 显然 还有更多的processing method可以用
	# return长这样:{'this': True, 'is':True, 'a':True, 'good':True, 'book':True}
	# 其中, 前一个叫fname, 对应每个出现的文本单词;
	# 后一个叫fval, 指的是每个文本单词对应的值。
	# 这里我们用最简单的True,来表示,这个词『出现在当前的句子中』的意义。
	# 当然啦, 我们以后可以升级这个方程, 让它带有更加牛逼的fval, 比如 word2vec
	return {word: True for word in s.lower().split()}

# 把训练集给做成标准形式
training_data = [[preprocess(s1), 'pos'],
				 [preprocess(s2), 'pos'],
				 [preprocess(s3), 'neg'],
				 [preprocess(s4), 'neg']]
print(training_data)
# 喂给model吃
model = NaiveBayesClassifier.train(training_data)
# 打出结果
print(model.classify(preprocess('this is a good book')))

"""用元素频率表示文本特征"""
# we you he work happy are
# 1 0 3 0 1 1
# 1 0 2 0 1 1
# 0 1 0 1 0 0

"""余弦定理"""

"""Frequency 频率统计"""















