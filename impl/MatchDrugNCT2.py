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

name_dict = "药品名称字典.xlsx"
name_dict_new = "{}{}".format("new_", name_dict)
name_dict_dealed = "drug_nct_dict_dealed.pkl"
field_dict_distinct = "以分号间隔的名称表"

path_dict = IOUtils.get_path_sources(name_dict)
path_dict_new = IOUtils.get_path_target(name_dict_new)
path_dict_dealed = IOUtils.get_path_target(name_dict_dealed)

field_source_remove = "clinicalTrialsGovIdentifier"
field_source_distinct = "intervention"
name_source = "NCT Drug（待匹配）.xlsx"
name_source_new = "{}{}".format("new_", name_source)
name_source_dealed = "drug_nct_source_dealed.pkl"

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
	# 获取长度大于1的元素
	result = {w for w in result if len(w) > 1}
	return result


def deal_dict(readcache=True):
	# readcache=False
	# 对数据进行去空格,转小写,拆分一行为多行
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
		rows = mydict.shape[0]  # 30515
		# index:前面的序号是否写到excel
		mydict.to_excel(path_dict_new, index=False)

	return mydict


def dealed_dict(mydict, readcache=True):
	# readcache = False
	# 字典数据清洗
	if readcache and IOUtils.exist_target(path_dict_dealed):
		# 从文件读取序列化文件
		with open(path_dict_dealed, "rb") as f:
			dict_dict = pickle.load(f)
	else:
		dict_dict = {}
		for txt in mydict.iloc[:, 1]:
			result = predeal(txt)
			if result:
				text = " ".join(result)
				weight = round(1 / len(result), 2)
				for w in result:
					if w in dict_dict:
						dd = dict_dict[w]
					else:
						dd = {}
						dict_dict[w] = dd
					dd[text] = weight

		# 保存sentences到文件
		with open(path_dict_dealed, "wb") as f:
			pickle.dump(dict_dict, f)

	return dict_dict


def deal_source(readcache=True):
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
		mysource = mysource[mysource[field_source_distinct].isnull().values == False]
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
		print(mysource.shape)
		mysource = mysource[mysource[field_source_distinct].isnull().values == False]
		print(mysource.shape)
		mysource.drop_duplicates(field_source_distinct, inplace=True)
		print(mysource.shape)
		mysource.to_excel(path_source_new, index=False)

	return mysource


def dealed_source(mysource, dict_dict, readcache=True):
	# readcache=False
	if readcache and IOUtils.exist_path(path_source_dealed):
		with open(path_source_dealed, "rb") as f:
			dealed = pickle.load(f)
	else:
		dealed = {}
		source_col = mysource.iloc[:, 1]
		for txt in source_col:
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

# mydict = deal_dict(readcache)
# dict_dict = dealed_dict(mydict,readcache)
mysource = deal_source(False)
exit()
# # dealed = dealed_source(mysource, dict_dict,readcache)
# dealed = dealed_source(mysource, dict_dict,False)
dealed = dealed_source(None, None, readcache)

result_right = []
result_error = []
for key_tuple, ls in dealed.items():
	dict_res = {}
	for dict_k in ls:
		for k, v in dict_k.items():
			if k in dict_res:
				k_tuple = dict_res[k]
				dict_res[k] = (k_tuple[0] + 1, k_tuple[1] + v)
			else:
				dict_res[k] = (1, v)

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
		pass
		# if lastweights > 1:
		# 	lastweights = 1.0
		# # 在待匹配药品中的相似度
		# weights = round(lasttimes / key_tuple[2], 2)
		# result_right.append(np.array((key_tuple[0], key_tuple[1], last, lasttimes, lastweights, weights)))
	else:
		lasttimes=0
		lastweights=0
		for k, k_tuple in dict_res.items():
			if k_tuple[0] > lasttimes and k_tuple[1] >= lastweights:
				lasttimes = k_tuple[0]
				lastweights = k_tuple[1]
				last = k
		# 在待匹配药品中的相似度
		weights = round(lasttimes / key_tuple[2], 2)
		result_error.append(np.array((key_tuple[0], key_tuple[1], last, lasttimes, lastweights, weights)))

# df = pd.DataFrame(result_right)
# df.columns = ["待匹配药品", "清洗後待匹配药品", "字典中匹配到药品", "待匹配药品和匹配到药品中相似的个数", "在匹配到药品中的相似度", "在待匹配药品中的相似度"]
# df.sort_values(by=["在待匹配药品中的相似度", "在匹配到药品中的相似度", "待匹配药品和匹配到药品中相似的个数"], ascending=False, inplace=True)
# df.to_excel(path_source_result_right, index=False)
df = pd.DataFrame(result_error)
df.columns = ["待匹配药品", "清洗後待匹配药品", "字典中匹配到药品", "待匹配药品和匹配到药品中相似的个数", "在匹配到药品中的相似度", "在待匹配药品中的相似度"]
df.sort_values(by=["在待匹配药品中的相似度", "在匹配到药品中的相似度", "待匹配药品和匹配到药品中相似的个数"], ascending=False, inplace=True)
df.to_excel(path_source_result_error, index=False)

print(1)
