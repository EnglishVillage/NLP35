# !/usr/bin/python3.5
# -*- coding:utf-8 -*-

import os, sys, re, time

sys.path.append("/home/esuser/NLP35")
import jieba, math
import numpy as np
import pandas as pd
from gensim.models import Word2Vec
from nltk import FreqDist

from utils import IOUtils
from utils import RegexUtils
from utils import StringUtils
try:
	import cPickle as pickle  # 序列化
except ImportError:
	import pickle

name_dict = "药品名称字典.xlsx"
name_dict_new = "{}{}".format("new_", name_dict)
name_dict_temp = "drug_nct_dict_temp.pkl"
name_dict_dealed = "drug_nct_dict_dealed.pkl"
field_dict_distinct = "以分号间隔的名称表"
field_dict_add = "分词後的词库字典"
field_dict_add2 = "分词後的词库字典的权重(在当前药品中的权重,在所有词库字典中的权重)"

path_dict = IOUtils.get_path_sources(name_dict)
path_dict_new = IOUtils.get_path_target(name_dict_new)
path_dict_temp = IOUtils.get_path_target(name_dict_temp)
path_dict_dealed = IOUtils.get_path_target(name_dict_dealed)


name_source = "NCT Drug（待匹配）.xlsx"
name_source_new = "{}{}".format("new_", name_source)
name_source_dealed = "drug_nct_source_dealed.pkl"

field_source_remove = "clinicalTrialsGovIdentifier"
field_source_distinct = "intervention"
field_source_add = "分词後的词库字典"

path_source = IOUtils.get_path_sources(name_source)
path_source_new = IOUtils.get_path_target(name_source_new)
path_source_dealed = IOUtils.get_path_target(name_source_dealed)

path_source_result_right = IOUtils.get_path_target("drug_nct_result(word_score).xlsx")
path_source_result_error = IOUtils.get_path_target("drug_nct_result(word_score)_error.xlsx")


def predeal(txt):
	# 替换中文字符为英文字符
	txt = StringUtils.replace_key(txt, RegexUtils.dict_zh_to_en_special_chars)
	# 提取括号里面内容
	tuple = RegexUtils.match(txt, *RegexUtils.set_match_special)
	ls = tuple[1]
	# 去掉括号【这里不用去掉，後面会一起去掉前後特殊字符】
	# for i, value in enumerate(ls):
	# 	ls[i] = RegexUtils.replace_diy_chars(value, "[(){}<>\[\]]+", "")
	# 合并成为一个集合
	ls.insert(0, tuple[0])
	# 替换一些字符为空格,并按空格切分,重新组合为集合
	result = []
	for value in ls:
		value = RegexUtils.replace_diy_chars(value, "[、+/]+", " ")
		# ,旁边如果有空格则去掉, 否则替换成空格
		if "," in value:
			while len(value) > 0 and value[0] == ",":
				value = value[1:]
			while len(value) > 0 and value[-1] == ",":
				value = value[:-1]
			if "," in value:
				value = value.replace(",", " ")
		result += value.split()
	# 去除开始和结束字符中的特殊字符
	for i, value in enumerate(result):
		while len(value) > 0 and not RegexUtils.re_wkz_all.findall(value[0]):
			value = value[1:]
		while len(value) > 0 and not RegexUtils.re_wkz_all.findall(value[-1]):
			value = value[:-1]
		value = RegexUtils.get_diy(value, RegexUtils.re_wkz_all_diy)
		result[i] = value
	# 获取长度不为空的元素
	temp = []
	for w in result:
		if w and w not in temp:
			temp.append(w)
	return temp


# 对字典进行去空格,转小写,拆分一行为多行,删除和去重
def deal_dict(readcache=True):
	if readcache and IOUtils.exist_path(path_dict_new):
		mydict = pd.read_excel(path_dict_new)
	else:
		mydict = pd.read_excel(path_dict)
		mydict.dropna(axis=0, how="any", inplace=True)
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
		mydict.dropna(axis=0, how="any", inplace=True)
		# 去重
		mydict.drop_duplicates(field_dict_distinct, inplace=True)
		# index:前面的序号是否写到excel
		mydict.to_excel(path_dict_new, index=False)

	return mydict


# 对字典进行分词且分词後按,进行连接并将结果存储到新列
def deal_dict2(mydict=None, readcache=True):
	if readcache and IOUtils.exist_path(path_dict_new):
		mydict = pd.read_excel(path_dict_new)
	else:
		if not mydict:
			mydict = deal_dict(True)

		# 获取字典那列数据
		onecol = mydict[field_dict_distinct]
		# 添加空白新列
		mydict[field_dict_add] = None
		# 对字典数据分词按,进行分割并将结果存储到新列
		for i, txt in enumerate(onecol):
			ls = predeal(txt)
			if ls:
				mydict[field_dict_add][i] = ",".join(ls)
		# index:前面的序号是否写到excel
		mydict.to_excel(path_dict_new, index=False)

	return mydict


# 对分词後的字典进行统计每个词的频数
def deal_dict3(mydict=None, readcache=True):
	if not mydict:
		mydict = deal_dict2(None, True)
	if readcache and IOUtils.exist_target(path_dict_temp):
		# 从文件读取序列化文件
		with open(path_dict_temp, "rb") as f:
			fdist = pickle.load(f)
	else:
		analysed_col = mydict[field_dict_add]
		# 将分词後的数据合并成为一个list
		ls_col = []
		for str_ls in analysed_col:
			ls_col += str_ls.split(",")
		# 统计分词後每个词的频数
		fdist = FreqDist(ls_col)
		# 所有词加上重复的个数
		# fdist.N()
		# 去重後的个数
		# len(fdist)
		with open(path_dict_temp, "wb") as f:
			pickle.dump(fdist, f)
	return mydict, fdist


# 获取不同数据类型的权重比
def get_type(w):
	try:
		float(w)
		return 0.2
	except:
		return 1


# 得到权重
def get_weight(total, curtimes, w):
	# 长度越长,tf_len越大
	tf_len = math.log(len(w) + 1)
	# 频数越大,idf越小
	idf = math.log(total / curtimes, 2)
	type = get_type(w)
	return round(tf_len * idf * type, 2)


# 计算字典分词後每个词的权重,按|进行连接并将结果存储到新列
def dealed_dict(t, readcache=True):
	if not t:
		t = deal_dict3(None, True)
	# 字典数据清洗
	if readcache and IOUtils.exist_target(path_dict_dealed):
		# 从文件读取序列化文件
		with open(path_dict_dealed, "rb") as f:
			dict_dict = pickle.load(f)
	else:
		dict_dict = {}
		fdist = t[1]
		total = fdist.N()
		mydict = t[0]
		analysed_col = mydict[field_dict_add]
		mydict[field_dict_add2] = None
		weight_ls = []
		weight_ls_2 = []
		for index, str_ls in enumerate(analysed_col):
			result = str_ls.split(",")
			if result:
				totalweight = 0
				weight_ls.clear()
				for w in result:
					weight = get_weight(total, fdist[w], w)
					totalweight += weight
					weight_ls.append(weight)
				text = " ".join(result)
				weight_ls_2.clear()
				for i, w in enumerate(result):
					if w in dict_dict:
						dd = dict_dict[w]
					else:
						dd = {}
						dict_dict[w] = dd
					weight = weight_ls[i]
					weight_new = round(weight / totalweight, 2)
					weight_total = (weight_new, weight)
					weight_ls_2.append(weight_total.__str__())
					mydict[field_dict_add2][index] = "|".join(weight_ls_2)
					dd[text] = weight_total

		# 保存
		with open(path_dict_dealed, "wb") as f:
			pickle.dump(dict_dict, f)
		mydict.to_excel(path_dict_new, index=False)

	return dict_dict


# 对数据进行去空格,转小写,拆分一行为多行,删除和去重
def deal_source(readcache=True):
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
		# 删除空数据
		mysource = mysource[mysource[field_source_distinct].isnull().values == False]
		print(mysource.shape)
		# 去重
		mysource.drop_duplicates(field_source_distinct, inplace=True)
		print(mysource.shape)
		rows = mysource.shape[0]  # 7340
		cols = mysource.shape[1]  # 2
		# 将待处理那列数据转化为字符串类型
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
		print(mysource.shape)
		mysource = mysource[mysource[field_source_distinct].isnull().values == False]
		print(mysource.shape)
		mysource.drop_duplicates(field_source_distinct, inplace=True)
		print(mysource.shape)
		mysource.to_excel(path_source_new, index=False)

	return mysource


# 对字典进行分词且分词後按,进行连接并将结果存储到新列
def deal_source2(mysource=None, readcache=True):
	if readcache and IOUtils.exist_target(path_source_new):
		mysource = pd.read_excel(path_source_new)
		mysource[field_source_add] = mysource[field_source_add].astype(str)
	else:
		if not mysource:
			mysource = deal_source(True)
		onecol = mysource.iloc[:, 1]
		mysource[field_source_add] = None
		for i, txt in enumerate(onecol):
			ls = predeal(txt)
			if ls:
				mysource[field_source_add][i] = ",".join(ls)
		# 删除空数据
		mysource = mysource[mysource[field_source_add].isnull().values == False]
		# 去重
		# mysource.drop_duplicates(field_source_add, inplace=True)
		print(mysource.shape)
		mysource[field_source_add] = mysource[field_source_add].astype(str)
		mysource.to_excel(path_source_new, index=False)
	return mysource


def dealed_source(mysource, dict_dict, readcache=True):
	if readcache and IOUtils.exist_path(path_source_dealed):
		with open(path_source_dealed, "rb") as f:
			dealed = pickle.load(f)
	else:
		if not mysource:
			mysource = deal_source(True)
		if not dict_dict:
			dict_dict = dealed_dict(None, True)

		onecol = mysource.iloc[:, 1]
		mysource[field_source_add] = None
		dealed = {}
		for i, txt in enumerate(onecol):
			ls = predeal(txt)
			if ls:
				ls_current = []
				for w in ls:
					dict_key = dict_dict.get(w, None)
					if dict_key:
						ls_current.append(dict_key)
				if ls_current:
					dealed[(txt, " ".join(ls), len(ls))] = ls_current
		# 保存
		with open(path_source_dealed, "wb") as f:
			pickle.dump(dealed, f)

	return dealed


readcache = True

# t = deal_dict3(None, True)
# mydict,fdist
# dict_dict = dealed_dict(None,readcache)
deal_source2(None,False)
exit()
dealed = dealed_source(None, None, readcache)

# temp={}
# i=0
# for key_tuple, ls in dealed.items():
# 	temp[key_tuple]=ls
# 	i+=1
# 	if i>20:
# 		break
# del dealed
# dealed=temp

result_right = []
result_error = []
for key_tuple, ls in dealed.items():
	dict_res = {}
	for dict_k in ls:
		for k, v in dict_k.items():
			if k in dict_res:
				k_tuple = dict_res[k]
				dict_res[k] = (k_tuple[0] + 1, k_tuple[1] + v[0])
			else:
				dict_res[k] = (1, v[0])

	# 待匹配药品和匹配到药品中相似的个数
	lasttimes = key_tuple[2] / 2
	# 在匹配到药品中的相似度
	lastweights = 0.5
	# 字典中匹配到药品
	last = None
	for k, k_tuple in dict_res.items():
		if k_tuple[0] > lasttimes and k_tuple[1] >= lastweights:
			lasttimes = k_tuple[0]
			lastweights = k_tuple[1]
			last = k
	if last:
		if lastweights > 1:
			lastweights = 1.0
		# 在待匹配药品中的相似度
		weights = round(lasttimes / key_tuple[2], 2)
		result_right.append(np.array((key_tuple[0], key_tuple[1], last, lasttimes, lastweights, weights)))
	else:
		lasttimes = 0
		lastweights = 0
		for k, k_tuple in dict_res.items():
			if k_tuple[0] > lasttimes and k_tuple[1] >= lastweights:
				lasttimes = k_tuple[0]
				lastweights = k_tuple[1]
				last = k
		# 在待匹配药品中的相似度
		weights = round(lasttimes / key_tuple[2], 2)
		result_error.append(np.array((key_tuple[0], key_tuple[1], last, lasttimes, lastweights, weights)))

df = pd.DataFrame(result_right)
df.columns = ["待匹配药品", "清洗後待匹配药品", "字典中匹配到药品", "待匹配药品和匹配到药品中相似的个数", "在匹配到药品中的相似度", "在待匹配药品中的相似度"]
df.sort_values(by=["在待匹配药品中的相似度", "在匹配到药品中的相似度", "待匹配药品和匹配到药品中相似的个数"], ascending=False, inplace=True)
df.to_excel(path_source_result_right, index=False)

df = pd.DataFrame(result_error)
df.columns = ["待匹配药品", "清洗後待匹配药品", "字典中匹配到药品", "待匹配药品和匹配到药品中相似的个数", "在匹配到药品中的相似度", "在待匹配药品中的相似度"]
df.sort_values(by=["在待匹配药品中的相似度", "在匹配到药品中的相似度", "待匹配药品和匹配到药品中相似的个数"], ascending=False, inplace=True)
df.to_excel(path_source_result_error, index=False)

print(1)
