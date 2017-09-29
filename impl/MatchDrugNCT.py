# !/usr/bin/python3.5
# -*- coding:utf-8 -*-
import jieba
import numpy as np
import pandas as pd
from gensim.models import Word2Vec

from utils import IOUtils
from utils import RegexUtils
from utils import StringUtils

try:
	import cPickle as pickle  # 序列化
except ImportError:
	import pickle

name_model = "word2vecNCT.model"
name_dict = "药品名称字典.xlsx"
name_dict_new = "{}{}".format("new_", name_dict)
name_sentences_dict = "drug_nct_dict.pkl"
field_dict_distinct= "以分号间隔的名称表"

path_model = IOUtils.get_path_target(name_model)
path_dict = IOUtils.get_path_sources(name_dict)
path_dict_new = IOUtils.get_path_target(name_dict_new)
path_sentences_dict = IOUtils.get_path_target(name_sentences_dict)

field_source_remove="clinicalTrialsGovIdentifier"
field_source_distinct="intervention"
name_source="NCT Drug（待匹配）.xlsx"
name_source_new="{}{}".format("new_", name_source)
name_sentences_source="drug_nct_source.pkl"

path_source=IOUtils.get_path_sources(name_source)
path_source_new=IOUtils.get_path_target(name_source_new)
path_sentences_source=IOUtils.get_path_target(name_sentences_source)
path_result=IOUtils.get_path_target("drug_nct_result(word2vec).xlsx")

readcache = True

def get_sentences(mydict):
	# 获取word2vec所需的句子【集合套集合,最外层不可以是生成器】
	sentences = []
	for txt in mydict.iloc[:, 1]:
		# 替换中文字符为英文字符
		review = StringUtils.replace_key(txt, RegexUtils.dict_zh_to_en_special_chars)
		# 提取括号里面内容
		tuple = RegexUtils.match(review, *RegexUtils.set_match_special)
		ls = tuple[1]
		# 去掉括号
		# for i, value in enumerate(ls):
		# 	ls[i] = RegexUtils.replace_diy_chars(value, "[(){}<>\[\]]+", "")
		# 合并成为一个集合
		ls.insert(0, tuple[0])
		# 替换一些字符为空格,并按空格切分,重新组合为集合
		result = []
		for value in ls:
			v1 = RegexUtils.replace_diy_chars(value, "[、+/]+", " ")
			# ,旁边如果有空格则去掉, 否则替换成空格
			if "," in v1:
				while len(v1) > 0 and v1[0] == ",":
					v1 = v1[1:]
				while len(v1) > 0 and v1[-1] == ",":
					v1 = v1[:-1]
				if "," in v1:
					v1 = v1.replace(",", " ")
			result += v1.split()
		# 去除开始和结束字符中的特殊字符
		for i, word in enumerate(result):
			while len(word) > 0 and not RegexUtils.re_wkz_all.findall(word[0]):
				word = word[1:]
			while len(word) > 0 and not RegexUtils.re_wkz_all.findall(word[-1]):
				word = word[:-1]
			word = RegexUtils.get_diy(word, RegexUtils.re_wkz_all_diy)
			result[i] = word
		# 获取长度大于1的元素
		result = [w for w in result if len(w) > 1]
		sentences.append(result)
	return sentences

def deal_dict():
	# readcache=False
	# 对数据进行去空格,转小写,拆分一行为多行
	if readcache and IOUtils.exist_target(name_dict_new):
		mydict = pd.read_excel(path_dict_new)
	else:
		mydict = pd.read_excel(path_dict)
		mydict.dropna(axis=0, how="any",inplace=True)
		mydict.drop_duplicates(field_dict_distinct, inplace=True)
		# print(mydict.count())
		# print(mydict.head())
		#          药品编码              以分号间隔的名称表
		# 0  M006159D01  卡培立肽;carperitide;卡哌利汀
		# 1  M006158D01                IW-1701
		# 2  M006157D01                IW-1973
		# 3  M006156D01  nelociguat;BAY60-4552
		# 4  M006155D01  cinaciguat;BAY58-2667
		rows = mydict.shape[0]  # 7340,7330
		cols = mydict.shape[1]  # 2
		mydict[field_dict_distinct] = mydict[field_dict_distinct].astype(str)
		for i, row in mydict.iterrows():
			ls = StringUtils.strip_and_lower_split_multiple_list(row[1], "；|;")
			if len(ls) > 1:
				for value in ls:
					mydict.loc[rows] = (row[0], value)
					rows += 1
				mydict.loc[i] = (row[0], None)
			else:
				mydict.loc[i] = (row[0], ls[0])
		# 删除前面设置为空的行
		mydict.dropna(axis=0, how="any",inplace=True)
		# 去重
		mydict.drop_duplicates(field_dict_distinct, inplace=True)
		rows = mydict.shape[0]  # 30515
		# index:前面的序号是否写到excel
		mydict.to_excel(path_dict_new, index=False)

	# readcache = False
	if readcache and IOUtils.exist_target(name_model):
		# 从文件读取序列化文件
		with open(path_sentences_dict, "rb") as f:
			sentences = pickle.load(f)
		model = Word2Vec.load(path_model)
	else:
		sentences = get_sentences(mydict)
		# 保存sentences到文件
		with open(path_sentences_dict, "wb") as f:
			pickle.dump(sentences, f)
		# 保存模型
		model = Word2Vec(sentences, size=200, min_count=1, workers=8)
		model.save(path_model)

	return sentences,model

def deal_source():
	# readcache=False
	# 对数据进行去空格,转小写,拆分一行为多行
	if readcache and IOUtils.exist_target(path_source_new):
		mysource = pd.read_excel(path_source_new)
		mysource[field_source_distinct] = mysource[field_source_distinct].astype(str)
	else:
		mysource = pd.read_excel(path_source)
		#   clinicalTrialsGovIdentifier            intervention
		# 0                 NCT03101150       400 IU Vitamin D3
		# 1                 NCT03101150      4000 IU Vitamin D3
		# 2                 NCT03069144   HAT1 topical solution
		# 3                 NCT03069144            Calcipotriol
		# 4                 NCT03071341                 AGT-181
		mysource=mysource[mysource[field_source_distinct].isnull().values==False]
		print(mysource.shape)
		mysource.drop_duplicates(field_source_distinct, inplace=True)
		print(mysource.shape)
		rows = mysource.shape[0]  # 7340
		cols = mysource.shape[1]  # 2
		mysource[field_source_distinct] = mysource[field_source_distinct].astype(str)
		for i, row in mysource.iterrows():
			ls = StringUtils.strip_and_lower_split_multiple_list(row[1], "；|;")
			if len(ls) > 1:
				for value in ls:
					mysource.loc[rows] = (row[0], value)
					rows += 1
				mysource.loc[i] = (row[0], None)
			else:
				mysource.loc[i] = (row[0], ls[0])
		mysource=mysource[mysource[field_source_distinct].isnull().values==False]
		mysource.drop_duplicates(field_source_distinct, inplace=True)
		mysource.to_excel(path_source_new, index=False)

	# readcache=False
	if readcache and IOUtils.exist_target(name_sentences_source):
		# 从文件读取序列化文件
		with open(path_sentences_source, "rb") as f:
			sentences = pickle.load(f)
	else:
		sentences=get_sentences(mysource)
		# 保存sentences到文件
		with open(path_sentences_source, "wb") as f:
			pickle.dump(sentences, f)

	return sentences

model=deal_dict()[1]
sentences=deal_source()
result=[]
for sentence in sentences:
	try:
		aa=model.most_similar(sentence)
		result.append(np.array([tuple(sentence),tuple(aa)]))
	except:
		pass

# model.
df=pd.DataFrame(result)
df.to_excel(path_result,index=False,header=False)



