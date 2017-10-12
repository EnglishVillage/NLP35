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
from nltk.classify import NaiveBayesClassifier  # 朴素贝叶斯分类器
from nltk import FreqDist  # 频率统计
from nltk.text import TextCollection

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


"""NLTK标注POS Tag【词性标注】"""
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

"""配上ML的情感分析【应用：文本相似度】"""
# # 随手造点训练集
# s1 = 'this is a good book'
# s2 = 'this is a awesome book'
# s3 = 'this is a bad book'
# s4 = 'this is a terrible book'
#
#
# def preprocess(s):
# 	# Func: 句子处理
# 	# 这里简单的用了split(), 把句子中每个单词分开
# 	# 显然 还有更多的processing method可以用
# 	# return长这样:{'this': True, 'is':True, 'a':True, 'good':True, 'book':True}
# 	# 其中, 前一个叫fname, 对应每个出现的文本单词;
# 	# 后一个叫fval, 指的是每个文本单词对应的值。
# 	# 这里我们用最简单的True,来表示,这个词『出现在当前的句子中』的意义。
# 	# 当然啦, 我们以后可以升级这个方程, 让它带有更加牛逼的fval, 比如 word2vec
# 	return {word: True for word in s.lower().split()}
#
#
# # 把训练集给做成标准形式
# training_data = [[preprocess(s1), 'pos'],
# 				 [preprocess(s2), 'pos'],
# 				 [preprocess(s3), 'neg'],
# 				 [preprocess(s4), 'neg']]
# print(training_data)
# # 喂给model吃
# model = NaiveBayesClassifier.train(training_data)
# # 打出结果
# print(model.classify(preprocess('this is a good book')))

"""用元素频率表示文本特征"""
# we you he work happy are
# 1 0 3 0 1 1
# 1 0 2 0 1 1
# 0 1 0 1 0 0

"""余弦定理"""

"""Frequency 频率统计【应⽤：⽂本分类】"""
# 做个词库先
corpus = 'this is my sentence this is my life this is the day'
# 随便tokenize⼀下
# 显然, 正如上文提到,
# 这里可以根据需要做任何的preprocessing:
# stopwords, lemma, stemming, etc.
tokens = nltk.word_tokenize(corpus)
# print(tokens)
# 得到token好的word list
# ['this', 'is', 'my', 'sentence', 'this', 'is', 'my', 'life', 'this', 'is', 'the', 'day']
# 借用NLTK的FreqDist统计一下文字出现的频率
fdist = FreqDist(tokens)
print(fdist)
# 所有词加上重复的个数
# fdist.N()
# 去重後的个数
# len(fdist)
# # 它就类似于一个Dict
# # 带上某个单词, 可以看到它在整个文章中出现的次数
# # print(fdist['is'])
# # 3
# # 好, 此刻, 我们可以把最常用的50个单词拿出来
# standard_freq_vector = fdist.most_common(50)
# size = len(standard_freq_vector)
# # print(size)
# # print(standard_freq_vector)
# # [('this', 3), ('is', 3), ('my', 2), ('sentence', 1), ('life', 1), ('the', 1), ('day', 1)]
# # Func: 按照出现频率大小, 记录下每一个单词的位置
# def position_lookup(v):
# 	res = {}
# 	counter = 0
# 	for word in v:
# 		res[word[0]] = counter
# 		counter += 1
# 	return res
# # 把标准的单词位置记录下来
# standard_position_dict = position_lookup(standard_freq_vector)
# print(standard_position_dict)
# # 得到一个位置对照表
# # {'this': 0, 'is': 1, 'my': 2, 'sentence': 3, 'life': 4, 'the': 5, 'day': 6}
# # 这时, 如果我们有个新句子:
# sentence = 'this is cool'
# # 先新建一个跟我们的标准vector同样大小的向量
# freq_vector = [0] * size
# # 简单的Preprocessing
# tokens = nltk.word_tokenize(sentence)
# # 对于这个新句子里的每一个单词
# for word in tokens:
# 	try:
# 		# 如果在我们的词库里出现过
# 		# 那么就在"标准位置"上+1
# 		freq_vector[standard_position_dict[word]] += 1
# 	except KeyError:
# 		# 如果是个新词
# 		# 就pass掉
# 		continue
# print(freq_vector)
# # [1, 1, 0, 0, 0, 0, 0]
# # 第一个位置代表 is, 出现了一次
# # 第二个位置代表 this, 出现了一次
# # 后面都木有

"""NLTK实现TF-IDF"""
# 首先, 把所有的文档放到TextCollection类中。
# 这个类会自动帮你断句, 做统计, 做计算
corpus = TextCollection(['this is sentence one', 'this is sentence two', 'this is sentence three'])
print(corpus._texts)
print(corpus)
# 直接就能算出tfidf
# (term: 一句话中的某个term, text: 这句话)
print(corpus.tf_idf('this', 'this is sentence four'))
# 0.444342
# 同理, 怎么得到一个标准大小的vector来表示所有的句子?
# 对于每个新句子
new_sentence = 'this is sentence five'
# 遍历一遍所有的vocabulary中的词:
# for word in standard_vocab:
# 	print(corpus.tf_idf(word, new_sentence))
	# 我们会得到一个巨长(=所有vocab长度)的向量
