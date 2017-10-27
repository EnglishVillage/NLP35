"""
清洗剂型规格
"""

import pandas as pd
import numpy as np
import re
import heapq
import Levenshtein as le

已上市药品规格地址 = r'F:\工作\中标剂型完善\剂型规格详情表5.xlsx'  # 请修改为实际地址
成分名异名表地址 = r'E:\我的招标项目数据\汇总工作表\药品名称清洗\成分名异名表v2.0.xlsx'  # 请修改为实际地址
pd_datamate2 = pd.read_excel(成分名异名表地址, sheetname='Sheet1')
pd_datamate3 = pd.read_excel(已上市药品规格地址)
params2 = {'毫': 'm', '升': 'l', '克': 'g', 'axa': '', '抗': '', '单位': 'iu', '微': 'u', 'μ': 'u', ' ': ''}
# 规格清洗预处理字典

pat = r'[\u4e00-\u9fa5]|[a-z]|[A-Z]|[0-9]'
pat2 = r'(^中国|爱尔兰|阿根廷|澳大利亚|巴西|生产厂|列支敦士登|美国|韩国|意大利|法国|无|德国|英国|日本|西班牙|比利时|印度|加拿大' \
	   r'|希腊|荷兰|波多黎各|墨西哥|新加坡|台湾|波兰|丹麦|瑞典|瑞士|冰岛)(\S+)'
pat3 = r'(山西|内蒙古|河北|安徽|4川|湖北|云南|天津|江西|江苏|浙江|湖南|吉林|黑龙江|' \
	   r'辽宁|上海|贵州|陕西|甘肃|广东|河南|新疆|山东|海南|北京|福建|宁夏|青海|军区|广西|重庆|西藏)(\S+)'
pat4 = r'(^\S+酸)(\S+)'
datapat = re.compile(pat)
datapat2 = re.compile(pat2)
datapat3 = re.compile(pat3)
datapat4 = re.compile(pat4)
p11 = r'[0-9]+\.?[0-9]*[mu]?[gl]'
p2 = r'[0-9](?=g)'
p21 = r'[0-9](?=ug)'
p3 = r'[0-9]l'
p31 = r'[0-9]+\.?[0-9]*ul'
p12 = r'[0-9]+\.?[0-9]*[mu]?g'
p13 = r'[0-9]+\.?[0-9]*[mu]?l'
p14 = r'[0-9]+\.?[0-9]*[w]?iu'
p4 = r'[0-9]+\.?[0-9]*wiu'
p5 = r'[0-9]+\.?[0-9]*(?=%)'
p6 = r'[0-9]+\.?[0-9]+$'


def most_match(item, tar):  # 最近字符距离函数
	def func(x):
		return le.jaro_winkler(str(item), str(x)), str(x)

	temp = map(func, tar)

	return max(temp)


def prefix(ps, parmas):  # 预处理替换函数
	i = str(ps)
	i = i.lower().strip()
	for k, v in parmas.items():
		i = i.replace(k, v)
	return i


def myds(x, y):  # 字符距离
	x = str(x)
	y = str(y)
	if x == '' and y == 'nan':
		return 0.5
	elif x == '' or y == 'nan':
		return 0
	else:
		try:
			return le.jaro(x, y)
		except:
			return 0


def mynds(x, y):  # 数字距离
	x = float(x)
	y = float(y)
	try:
		return 1 - (abs(x - y) / (x + y))
	except:
		return 0


def myn2ds(x, y):  # 数字距离2
	try:
		x1 = set(str(x).split())
		x1.add(str(sum(heapq.nsmallest(2, set(map(float, x1))))))
		y1 = set(str(y).split())
		y1.add(str(sum(heapq.nsmallest(2, set(map(float, y1))))))
		x1 = set(map(float, x1))
		y1 = set(map(float, y1))
		return len(x1 & y1) / len(x1 | y1)
	except:
		return 0


def mydds(x, y):  # 剂型距离
	try:
		x = set(x) - set('剂')
		y = set(y) - set('剂')
		if x & set('粉针'):
			x = x | set('冻干')
		if ('注' in x) & ('射' in x) & ('用' in x):
			x = set('注射(冻干)')
		if x & set('冻针'):
			x = x | set('注')
		if x & set('搽'):
			x = x | set('外')
		if x & set('冲'):
			x = x | set('颗粒')
		return len(x & y) / len(x | y)
	except:
		return 0


def 规格提取(s, flag=1):
	# flag = 1 提取全部剂型，flag =2 只提取mg，flag=3 只提取ml flag=4 只提取IU flag=5 只提取百分比

	out2 = set()
	if flag == 1:
		out = re.findall(p11, str(s).lower())
		for i in out:
			if re.search(p2, i):
				j = str(int(float(i.strip('g')) * 1000)) + 'mg'
			elif re.search(p3, i):
				j = str(int(float(i.strip('l')) * 1000)) + 'ml'
			elif re.search(p21, i):
				j = str(float(i.strip('ug')) / 1000) + 'mg'
			else:
				j = i
			out2 |= set([format(j, '.2f')])
		return ' '.join(out2)
	if flag == 2:
		out = re.findall(p12, str(s).lower())
		for i in out:
			if re.search(p2, i):
				j = float(i.strip('g')) * 1000  # + 'mg'
			elif re.search(p21, i):
				j = float(i.strip('ug')) / 1000  # + 'mg'
			else:
				j = float(i.strip('mg'))
			out2 |= set([format(j, '.2f')])
		return ' '.join(out2)
	if flag == 3:
		out = re.findall(p13, str(s).lower())
		# print(out)
		for i in out:
			# print(i)
			if re.search(p3, i):
				j = float(i.strip('l')) * 1000  # + 'ml'
			elif re.search(p31, i):
				j = float(i.strip('ul')) / 1000  # + 'mg'
			else:
				j = float(i.strip('ml'))
			out2 |= set([format(j, '.2f')])
		return ' '.join(out2)
	if flag == 4:
		out = re.findall(p14, str(s).lower())
		for i in out:
			if re.search(p4, i):
				j = float(i.strip('wiu')) * 10000
			else:
				j = float(i.strip('iu'))
			out2 |= set([format(j, '.2f')])
		return ' '.join(out2)

	if flag == 5:
		out = re.findall(p5, str(s).lower())
		out3 = re.findall(p6, str(s).lower())
		out4 = re.findall(p12, str(s).lower())
		out5 = re.findall(p13, str(s).lower())
		for i in out:
			j = format(float(i), '.2f')
			out2 |= set([j])
		for i in out3:
			j = format(float(i) * 100, '.2f')
			out2 |= set([j])
		for m in out5:  # 将mg ml转换为%比浓度
			if re.search(p3, m):
				k = float(m.strip('l')) * 1000  # + 'ml'
			elif re.search(p31, m):
				k = float(m.strip('ul')) / 1000  # + 'mg'
			else:
				k = float(m.strip('ml'))
			for i in out4:
				if re.search(p2, i):
					j = float(i.strip('g')) * 1000  # + 'mg'
				elif re.search(p21, i):
					j = float(i.strip('ug')) / 1000  # + 'mg'
				else:
					j = float(i.strip('mg'))
				if k:
					j = j / (k * 10)
				else:
					j = 0
				out2 |= set([format(j, '.2f')])
	if flag == 6:
		out2 = re.findall(p6, str(s).lower())
		return ' '.join(out2)
	return ' '.join(out2)


def 清洗成分名(dfD):
	if '通用名' not in dfD.columns.values:
		dfD['通用名'] = np.nan
	if '剂型' not in dfD.columns.values:
		dfD['剂型'] = np.nan
	if '规格' not in dfD.columns.values:
		dfD['规格'] = np.nan
	dfD = dfD[['通用名', '剂型', '规格']]  # 只取通用名、剂型、规格三个字段
	魔方产品名称列表 = set(pd_datamate2['异名'])
	dfD['通用名2'] = dfD['通用名'].apply(lambda x: ''.join(datapat.findall(str(x))))
	dfD['通用名2'] = dfD['通用名2'].apply(lambda x: datapat4.sub(r'\2\1', str(x).lower()))
	待匹配产品名称列表 = set(dfD['通用名2'])
	药品字典输出 = {}
	for key in 待匹配产品名称列表 & 魔方产品名称列表:
		药品字典输出[key] = (1, key)

	for key in 待匹配产品名称列表 - 魔方产品名称列表:
		药品字典输出[key] = most_match(key, 魔方产品名称列表)

	df = pd.DataFrame(药品字典输出).T
	df = df.reset_index()
	df.columns = ['待匹配', '匹配度', '匹配结果']
	dfH = pd.merge(df, pd_datamate2, left_on='匹配结果', right_on='异名', how='left')
	dfH = dfH.loc[dfH['匹配度'] > 0.75]
	dfF = pd.merge(dfD, dfH, left_on='通用名2', right_on='待匹配', how='left')
	dfF['成分名'] = dfF['成分名'].fillna(dfF['通用名'])
	dfF = dfF.drop(['待匹配', '匹配度', '匹配结果', '异名', '通用名2'], axis=1, errors='ignore')
	return dfF


def 药品剂型规格清洗(dfA):
	dfC = pd_datamate3
	dfA['剂型'] = dfA['剂型'].fillna(dfA['通用名'])
	dfA['剂型'] = dfA['剂型'].apply(lambda x: ''.join(datapat.findall(str(x))))
	dfB = dfA[['通用名', '剂型', '规格', '成分名']]
	dfB = dfB.drop_duplicates()
	dfB['规格2'] = dfB['规格'].apply(prefix, args=(params2,))
	dfB['规格-mg'] = dfB['规格2'].apply(规格提取, args=(2,))
	dfB['规格-ml'] = dfB['规格2'].apply(规格提取, args=(3,))
	dfB['规格-iu'] = dfB['规格2'].apply(规格提取, args=(4,))
	dfB['规格-%'] = dfB['规格2'].apply(规格提取, args=(5,))
	del dfB['规格2']
	dfD = pd.merge(dfB.reset_index(), dfC, on='成分名', how='left')
	dfD = dfD.set_index(['index', 'indexB'])
	s1 = pd.Series(map(mydds, dfD['通用名_x'], dfD['剂型_y']), index=dfD.index)
	s2 = pd.Series(map(mydds, dfD['剂型_x'], dfD['剂型_y']), index=dfD.index)
	s4 = pd.Series(map(myn2ds, dfD['规格-mg_x'], dfD['规格-mg_y']), index=dfD.index)
	s5 = pd.Series(map(myn2ds, dfD['规格-ml_x'], dfD['规格-ml_y']), index=dfD.index)
	s6 = pd.Series(map(myn2ds, dfD['规格-iu_x'], dfD['规格-iu_y']), index=dfD.index)
	s7 = pd.Series(map(myn2ds, dfD['规格-%_x'], dfD['规格-%_y']), index=dfD.index)
	dfout = pd.concat([s1, s2, s4, s5, s6, s7], axis=1, ignore_index=1)
	dfout.columns = ['辅助剂型匹配度', '剂型匹配度', '规格_mg', '规格_ml', '规格_iu', '规格_%']
	dfE = pd.concat([dfD, dfout], axis=1)
	dfE = dfE.drop(['规格-mg_x', '规格-mg_y', '规格-ml_x', '规格-ml_y', '规格-iu_x', '规格-iu_y', '规格-%_x', '规格-%_y'], axis=1,
				   errors='ignore')
	dfE['排序依据'] = dfE[['规格_mg', '规格_ml', '规格_iu', '规格_%']].max(axis=1) + (dfE['规格_mg'] * 1.0 + dfE['规格_ml'] * 1.0 + dfE[
		'规格_iu'] * 1.0 + dfE['规格_%'] * 1.0) * 0.3 + dfE['剂型匹配度'] * 1.3 + dfE['辅助剂型匹配度'] * 2  # 排序权重
	dfE = dfE.groupby(level=0).apply(lambda dfout: dfout.sort_values(by='排序依据')[-1:])
	dfE = dfE.reset_index('indexB')[['通用名_x', '通用名_y', '剂型_x', '规格_x', '成分名', '剂型_y', '规格_y', 'indexB']]
	dfE = pd.merge(dfA, dfE, left_on=['通用名', '剂型', '规格', '成分名'], right_on=['通用名_x', '剂型_x', '规格_x', '成分名'], how='left')
	dfE = dfE.drop(['通用名_x', '剂型_x', '剂型N', '规格_x', '规格N'], axis=1, errors='ignore')
	dfE = dfE.rename(columns={'剂型_y': '剂型N', '规格_y': '规格N', '通用名_y': '通用名N'})
	return dfE


'''
调用方式：
药品剂型规格清洗(清洗成分名(dfA))

'''
