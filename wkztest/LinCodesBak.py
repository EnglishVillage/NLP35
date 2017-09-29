"""
小林的代码
"""

import pandas as pd
import numpy as np
import re
import Levenshtein as le
from datetime import timedelta

待合并文件1地址 = r'E:\我的招标项目数据\汇总工作表\汇总测试2017-8-31.csv'
# 待合并文件2地址 = r'E:\我的招标项目数据\汇总工作表\汇总测试.csv'
待合并文件2地址 = r'E:\我的招标项目数据\数据更新\数据更新2017-8-31.csv'
待审核企业异名地址 = r'E:\我的招标项目数据\汇总工作表\企业名称清洗\企业名称匹配结果.xlsx'
审核完成企业异名地址 = r'E:\我的招标项目数据\汇总工作表\企业名称清洗\企业名称匹配结果2.xlsx'
待审核产品异名地址 = r'E:\我的招标项目数据\汇总工作表\药品名称清洗\成分名匹配结果.xlsx'
审核完成产品异名地址 = r'E:\我的招标项目数据\汇总工作表\药品名称清洗\成分名匹配结果2.xlsx'
已上市药品规格地址 = r'E:\我的招标项目数据\汇总工作表\剂型规格清洗\已上市药品成分名规格-细化规格2.xlsx'
企业异名字典地址 = r'F:\工作\企业名称清洗流程\成果表\企业异名字典V1.6.xlsx'
成分名异名表地址 = r'E:\我的招标项目数据\汇总工作表\药品名称清洗\成分名异名表v2.0.xlsx'
商品名字典地址 = r'E:\我的招标项目数据\汇总工作表\商品名工作表\商品名成果表2.xlsx'

pd_datamate = pd.read_excel(企业异名字典地址, sheetname='Sheet1')  # 企业异名
pd_datamate2 = pd.read_excel(成分名异名表地址, sheetname='Sheet1')
pd_datamate3 = pd.read_excel(商品名字典地址, sheetname='Sheet1')

params = {'省': '', '市': '', '股份有限公司': '', '有限公司': '', '有限责任公司': '', '经济特区': '', '广西壮族自治区': '广西', '西藏自治区': '西藏', '宁夏回族自治区': '宁夏', '内蒙古自治区': '内蒙古', '新疆维吾尔自治区': '新疆', '宁夏回族自治区': '宁夏', '阿坝藏族羌族自治区': '阿坝', '生产企业': '', '委托方': '', '葯': '药', '：': ':', '〇': '0', '零': '0', '一': '1', '二': '2', '三': '3', '四': '4', '五': '5', '六': '6', '七': '7', '八': '8', '九': '9', '委托方': '', '会社': ''}  # 企业名称清洗预处理字典
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
		x = float(x)
		y = float(y)
		if x == y:
			return 1
		else:
			return 0
	except:
		return myds(x, y)


def mydds(x, y):  # 剂型距离
	try:
		x = set(x) - set('剂')
		if x & set('冻针'):
			x = x | set('注射液')
		if x & set('搽'):
			x = x | set('外用液体')
		if x & set('冲'):
			x = x | set('颗粒')
		y = set(y) - set('剂')
		if len(x & y) > 0:
			return 1
		else:
			return 0
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


def 文件合并(dfA, dfB):
	print('开始合并文件...' '\n', 待合并文件1地址, '\n', 待合并文件2地址)
	dfA = dfA.drop(['预留字段1', '预留字段2', '预留字段3', 'flag', 'indexB'], axis=1, errors='ignore')
	dfB = dfB.drop(['预留字段1', '预留字段2', '预留字段3', 'flag', 'indexB'], axis=1, errors='ignore')
	dfC = pd.concat([dfA, dfB])
	if '索引' in dfC.columns.values:
		indexmax = int(dfC['索引'].max())
	else:
		indexmax = 0
		dfC['索引'] = np.nan
	indexadd = len(dfC[pd.isnull(dfC['索引'])])
	addindex = range((indexmax + 1), int(indexmax + indexadd + 1))
	dfC.loc[pd.isnull(dfC['索引']), '索引'] = addindex
	dfC['生产企业N'] = dfC['生产企业']
	print('文件合并完成')
	return dfC


def 企业名称匹配(dfA):
	print('开始企业名称匹配...')
	print('企业名称字典为', '\n', 企业异名字典地址)
	dfA['异名'] = dfA['生产企业N']
	dfA['异名'] = dfA['异名'].apply(lambda x: ''.join(datapat.findall(str(x))))
	dfA['异名'] = dfA['异名'].apply(prefix, args=(params,))
	dfA['异名'] = dfA['异名'].apply(lambda x: datapat2.sub(r'\2\1', str(x)))
	dfA['异名'] = dfA['异名'].apply(lambda x: datapat3.sub(r'\2\1', str(x)))
	print('企业名称预处理完成')
	魔方企业名称列表 = set(pd_datamate['异名'])
	待匹配企业名称列表 = set(dfA['异名'])
	药品字典输出 = {}
	for key in 待匹配企业名称列表 & 魔方企业名称列表:
		药品字典输出[key] = (1, key)
	print('企业名称精确匹配完成')
	print('开始企业名称模糊匹配，请耐心等待...')
	for key in 待匹配企业名称列表 - 魔方企业名称列表:
		药品字典输出[key] = most_match(key, 魔方企业名称列表)
	print('企业名称最佳模糊匹配完成')
	df = pd.DataFrame(药品字典输出).T
	df = df.reset_index()
	df.columns = ['待匹配', '匹配度', '匹配结果']
	df.to_excel(待审核企业异名地址, index=False)  # 输出企业名称匹配结果
	print('已经企业名称匹配结果输出至：', 待审核企业异名地址)
	print('等待人工审核匹配结果')


def 企业名称清洗(dfA, path):
	print('开始企业名称清洗...')
	print('企业名称清洗对照表为：', '\n', path)
	dfA['异名'] = dfA['生产企业N']
	dfA['异名'] = dfA['异名'].apply(lambda x: ''.join(datapat.findall(str(x))))
	dfA['异名'] = dfA['异名'].apply(prefix, args=(params,))
	dfA['异名'] = dfA['异名'].apply(lambda x: datapat2.sub(r'\2\1', str(x)))
	dfA['异名'] = dfA['异名'].apply(lambda x: datapat3.sub(r'\2\1', str(x)))
	dfB = pd.read_excel(path, sheetname='Sheet1')
	dfB = dfB.loc[dfB['匹配度'] > 0.75]
	dfC = pd.merge(dfB, pd_datamate, left_on='匹配结果', right_on='异名')
	dfC = dfC[['待匹配', '基础名', '匹配度', 'flag']]
	dfD = pd.merge(dfA, dfC, left_on='异名', right_on='待匹配', how='left')
	dfD = dfD.drop(['异名', '待匹配', '匹配度'], axis=1, errors='ignore')
	dfD['基础名'] = dfD['基础名'].fillna(dfD['生产企业N'])
	dfD = dfD.drop(['生产企业N'], axis=1, errors='ignore')
	dfD = dfD.rename(columns={'基础名': '生产企业N'})
	# dfD.loc[(pd.isnull(dfD['flag']))&(dfD['生产企业N'].str.contains(r'[a-z]',case=0,na=False)),'flag']=1
	# dfD['flag'] = dfD['flag'].fillna(0)
	print('完成企业名称清洗')
	return dfD


def 药品名称匹配(dfD):
	print('开始药品名称匹配...')
	print('药品名称字典为', '\n', 成分名异名表地址)
	魔方产品名称列表 = set(pd_datamate2['异名'])
	dfD['通用名2'] = dfD['通用名'].apply(lambda x: ''.join(datapat.findall(str(x))))
	dfD['通用名2'] = dfD['通用名2'].apply(lambda x: datapat4.sub(r'\2\1', str(x).lower()))
	print('药品名称预处理完成')
	待匹配产品名称列表 = set(dfD['通用名2'])
	药品字典输出 = {}
	for key in 待匹配产品名称列表 & 魔方产品名称列表:
		药品字典输出[key] = (1, key)
	print('药品名称精确匹配完成')
	print('开始药品名称模糊匹配，请耐心等待...')
	for key in 待匹配产品名称列表 - 魔方产品名称列表:
		药品字典输出[key] = most_match(key, 魔方产品名称列表)
	print('药品名称最佳模糊匹配完成')
	df = pd.DataFrame(药品字典输出).T
	df = df.reset_index()
	df.columns = ['待匹配', '匹配度', '匹配结果']
	df.to_excel(待审核产品异名地址, index=False)  # 输出产品名称匹配结果
	print('已经产品名称匹配结果输出至：', 待审核产品异名地址)
	print('等待人工审核匹配结果')


def 药品名称清洗(dfD, path):
	print('开始药品名称清洗...')
	print('药品名称清洗对照表为：', '\n', path)
	dfD = dfD.drop(['成分名'], axis=1, errors='ignore')
	dfD['通用名2'] = dfD['通用名'].apply(lambda x: ''.join(datapat.findall(str(x))))
	dfD['通用名2'] = dfD['通用名2'].apply(lambda x: datapat4.sub(r'\2\1', str(x).lower()))
	dfE = pd.read_excel(path, sheetname='Sheet1')
	dfH = pd.merge(dfE, pd_datamate2, left_on='匹配结果', right_on='异名', how='left')
	dfH = dfH.loc[dfH['匹配度'] > 0.75]
	dfF = pd.merge(dfD, dfH, left_on='通用名2', right_on='待匹配', how='left')
	dfF['成分名'] = dfF['成分名'].fillna(dfF['通用名'])
	dfF = dfF.drop(['待匹配', '匹配度', '匹配结果', '异名', '通用名2'], axis=1, errors='ignore')
	print('完成药品名称清洗')
	return dfF


def 药品剂型规格清洗(dfA, path):
	print('开始药品剂型规格清洗...')
	print('药品剂型规格清洗对照表为：', '\n', path)
	dfA['剂型'] = dfA['剂型'].fillna(dfA['通用名'])
	dfB = dfA[['剂型', '规格', '成分名']]
	dfB = dfB.drop_duplicates()
	dfC = pd.read_excel(path, sheetname='Sheet1')
	dfB['规格2'] = dfB['规格'].apply(prefix, args=(params2,))
	dfB['规格-mg'] = dfB['规格2'].apply(规格提取, args=(2,))
	dfB['规格-ml'] = dfB['规格2'].apply(规格提取, args=(3,))
	dfB['规格-iu'] = dfB['规格2'].apply(规格提取, args=(4,))
	dfB['规格-%'] = dfB['规格2'].apply(规格提取, args=(5,))
	del dfB['规格2']
	print('建立所有可能匹配组合...')
	dfD = pd.merge(dfB.reset_index(), dfC, on='成分名', how='left')
	dfD = dfD.set_index(['index', 'indexB'])
	s2 = pd.Series(map(mydds, dfD['剂型_x'], dfD['剂型_y']), index=dfD.index)
	s4 = pd.Series(map(myn2ds, dfD['规格-mg_x'], dfD['规格-mg_y']), index=dfD.index)
	s5 = pd.Series(map(myn2ds, dfD['规格-ml_x'], dfD['规格-ml_y']), index=dfD.index)
	s6 = pd.Series(map(myn2ds, dfD['规格-iu_x'], dfD['规格-iu_y']), index=dfD.index)
	s7 = pd.Series(map(myn2ds, dfD['规格-%_x'], dfD['规格-%_y']), index=dfD.index)
	dfout = pd.concat([s2, s4, s5, s6, s7], axis=1, ignore_index=1)
	dfout.columns = ['剂型匹配度', '规格_mg', '规格_ml', '规格_iu', '规格_%']
	dfE = pd.concat([dfD, dfout], axis=1)
	dfE = dfE.drop(['规格-mg_x', '规格-mg_y', '规格-ml_x', '规格-ml_y', '规格-iu_x', '规格-iu_y', '规格-%_x', '规格-%_y'], axis=1,
				   errors='ignore')
	dfE['排序依据'] = dfE[['规格_mg', '规格_ml', '规格_iu', '规格_%']].max(axis=1) + (dfout['规格_mg'] * 1.2 + dfout['规格_ml'] * 1.0 +
																		  dfout['规格_iu'] * 1.2 + dfout[
																			  '规格_%'] * 1.0) * 0.3 + dfout[
																										 '剂型匹配度'] * 1.3  # 排序权重
	print('开始寻找最佳匹配...')
	dfF = dfE.groupby(level=0).apply(lambda dfout: dfout.sort_values(by='排序依据')[-1:])
	dfG = dfF.reset_index('indexB')[['剂型_x', '规格_x', '成分名', '剂型_y', '规格_y', 'indexB']]
	dfH = pd.merge(dfA, dfG, left_on=['剂型', '规格', '成分名'], right_on=['剂型_x', '规格_x', '成分名'], how='left')
	dfH = dfH.drop(['剂型_x', '剂型N', '规格_x', '规格N'], axis=1, errors='ignore')
	dfH = dfH.rename(columns={'剂型_y': '剂型N', '规格_y': '规格N'})
	print('药品剂型规格清洗完成')
	return dfH


def 转换比清洗(dfA):
	print('开始转换比清洗...')
	dfA = dfA.drop(['转换比N'], axis=1, errors='ignore')
	dfB = dfA[['成分名', '剂型N', '规格N', '转换比', '生产企业N']]
	dfB2 = dfA[['成分名', '剂型N', '规格N', '转换比', '价格', '生产企业N']].drop_duplicates()
	dfC = dfB.groupby(['成分名', '剂型N', '规格N', '转换比', '生产企业N']).apply(lambda dfout: len(dfout)).reset_index()
	dfC = dfC.rename(columns={0: '企业成分名转换比数'})
	dfC2 = dfB.groupby(['成分名', '剂型N', '转换比']).apply(lambda dfout: len(dfout)).reset_index()
	dfC2 = dfC2.rename(columns={0: '成分名转换比数'})
	dfC3 = dfB.groupby(['成分名', '剂型N']).apply(lambda dfout: len(dfout)).reset_index()
	dfC3 = dfC3.rename(columns={0: '成分名剂型数'})
	dfC4 = dfB.groupby(['转换比']).apply(lambda dfout: len(dfout)).reset_index()
	dfC4 = dfC4.rename(columns={0: '转换比数'})
	dfD = pd.merge(pd.merge(pd.merge(dfC, dfC2), dfC3), dfC4)
	dfE = dfD.loc[(((dfD['成分名转换比数'] / dfD['成分名剂型数']) < 0.04) & ((dfD['转换比数']) < 500)) | ((dfD['转换比数']) < 200) | (
		(dfD['转换比']) > 2000)]
	dfE = dfE[['成分名', '剂型N', '规格N', '转换比', '生产企业N']]
	dfE = pd.merge(dfE, dfB2, how='left')
	dfB1 = dfB2.loc[pd.isnull(dfB2['转换比'])].drop_duplicates()
	dfF = pd.concat([dfB1, dfE], axis=0)
	dfH = pd.merge(dfF.reset_index(), dfB2.reset_index(), on=['生产企业N', '成分名', '剂型N', '规格N'])
	dfH = dfH.loc[(dfH['转换比_x'] != dfH['转换比_y']) & (pd.isnull(dfH['转换比_y']) == False)]
	dfI = dfH.set_index(['index_x', 'index_y'])
	s2 = pd.Series(map(mynds, dfI['价格_x'], dfI['价格_y']), index=dfI.index)
	dfJ = pd.concat([dfI, s2], axis=1)
	dfK = dfJ.groupby(level=0).apply(lambda dfout: dfout.sort_values(by=0)[-1:])
	dfK.loc[(dfK['成分名'] == '叶酸') & (dfK['转换比_x'] == 62), '转换比_y'] = 62
	dfK.loc[dfK['转换比_x'] == 122, '转换比_y'] = 24
	dfL = dfK[['价格_x', '剂型N', '成分名', '生产企业N', '规格N', '转换比_x', '转换比_y']]
	dfL = dfL.rename(columns={'价格_x': '价格', '转换比_x': '转换比', '转换比_y': '转换比N'})
	dfK = pd.merge(dfA, dfL, how='left')
	dfK['转换比N'] = dfK['转换比N'].fillna(dfK['转换比'])
	print('转换比清洗完成')
	return dfK


def 单位价格清洗(dfA):
	print('开始单位价格清洗')
	dfA['单位价格'] = dfA['价格'] / dfA['转换比N']
	dfB = dfA[['成分名', '剂型N', '规格N', '转换比N', '单位价格', 'flag', '项目名称']].dropna()
	dfB = dfB.drop_duplicates(['成分名', '剂型N', '规格N', '单位价格', '转换比N', 'flag', '项目名称'])
	dfB = dfB[['成分名', '剂型N', '规格N', '转换比N', '单位价格', 'flag']]
	dfC = dfB.groupby(['成分名', '剂型N', '规格N', 'flag']).apply(lambda dfout: dfout['单位价格'].dropna().quantile(0.55))
	dfD = dfB.groupby(['成分名', '剂型N', '规格N', 'flag']).apply(lambda dfout: dfout['单位价格'].dropna().quantile(0.45))
	dfE = pd.concat([dfC, dfD], axis=1, ignore_index=1).reset_index()
	dfF = pd.merge(dfA, dfE, how='left')
	dfF.loc[(dfF['价格状态'] == '每日限价') | (dfF['价格状态'] == '医保最高销售限价') | (dfF['价格状态'] == '医保支付结算价'), '单位价格'] = np.nan
	dfH = dfF
	dfH = dfH.rename(columns={0: '7分位', 1: '3分位'})
	s2 = pd.Series(map(mynds, dfH['价格'], dfH['7分位']), index=dfH.index)
	s3 = pd.Series(map(mynds, dfH['单位价格'], dfH['3分位']), index=dfH.index)
	dfH = pd.concat([dfH, s2, s3], axis=1)
	dfH = dfH.rename(columns={0: 'test', 1: 'test2'})
	dfH.loc[dfH['test'] > dfH['test2'], '单位价格N'] = dfH['价格']
	dfH.loc[dfH['test'] <= dfH['test2'], '单位价格N'] = dfH['单位价格']
	dfH = dfH.drop(['单位价格', '7分位', '3分位', 'test', 'test2'], axis=1, errors='ignore')
	# dfH = dfH.drop(['单位价格'],axis=1,errors='ignore')
	dfH = dfH.rename(columns={'单位价格N': '单位价格'})
	dfH.loc[dfH['索引'] == 1284634, '单位价格'] = 17.89  # 特殊处理某条记录的单位价格
	print('单位价格清洗完成')
	return dfH


def 商品名清洗(dfA):
	print('开始商品名清洗...')
	dfA = dfA.drop(['商品名'], axis=1, errors='ignore')
	dfB = pd_datamate3
	dfC = pd.merge(dfA, dfB, how='left')
	print('商品名清洗完成')
	return dfC


def 同商品名企业名称修正(dfA):
	print('开始其他修正...')
	dfB = dfA[['成分名', '生产企业N', '商品名']]
	dfB = dfB.dropna()
	dfB['sum'] = 1
	dfC = dfB.groupby(['成分名', '生产企业N', '商品名'], as_index=False)
	dfC = dfC.sum()
	dfC = dfC.sort_values(by='sum', ascending=0)
	dfD = dfC.drop_duplicates(['成分名', '商品名'])
	dfE = pd.merge(dfA, dfD, on=['成分名', '商品名'], how='left')
	dfE['生产企业N'] = dfE['生产企业N_y'].fillna(dfE['生产企业N_x'])
	dfE = dfE.drop(['sum', '生产企业N_x', '生产企业N_y'], axis=1, errors='ignore')
	print('清洗完成...等待结果输出')
	return dfE


def 发现价格异常(dfA):
	print('寻找异常单价价格的记录...')
	dfB = dfA[['生产企业N', '成分名', '剂型N', '规格N', '单位价格']]
	dfC = dfB.groupby(['生产企业N', '成分名', '剂型N', '规格N']).median()
	dfC = dfC.reset_index()
	dfC = dfC.rename(columns={'单位价格': '价格中值'})
	dfA = pd.merge(dfA, dfC, how='left')
	dfA['异常指标'] = dfA['单位价格'] / dfA['价格中值']
	dfAA = dfA.loc[(dfA['异常指标'] > 5) | (dfA['异常指标'] < 0.2)]
	print('找到异常单价异常记录', len(dfAA), '条')
	return dfAA


def 根据异常价格清洗转换比(dfA, dfAA):
	print('根据异常价格清洗转换比....')
	dfB2 = dfA[['成分名', '剂型N', '规格N', '转换比', '价格', '生产企业N']].drop_duplicates()
	dfE = dfAA[['成分名', '剂型N', '规格N', '转换比', '生产企业N', '价格']].drop_duplicates()
	dfH = pd.merge(dfE.reset_index(), dfB2.reset_index(), on=['生产企业N', '成分名', '剂型N', '规格N'])
	dfH = dfH.loc[(dfH['转换比_x'] != dfH['转换比_y']) & (pd.isnull(dfH['转换比_y']) == False)]
	dfI = dfH.set_index(['index_x', 'index_y'])
	s2 = pd.Series(map(mynds, dfI['价格_x'], dfI['价格_y']), index=dfI.index)
	dfJ = pd.concat([dfI, s2], axis=1)
	print('开始寻找异常单价记录最可能的转换比')
	dfK = dfJ.groupby(level=0).apply(lambda dfout: dfout.sort_values(by=0)[-1:])
	dfL = dfK[['价格_x', '剂型N', '成分名', '生产企业N', '规格N', '转换比_x', '转换比_y']]
	dfL = dfL.rename(columns={'价格_x': '价格', '转换比_x': '转换比N', '转换比_y': '转换比M'})
	dfK = pd.merge(dfA, dfL, how='left')
	dfK['转换比M'] = dfK['转换比M'].fillna(dfK['转换比N'])
	dfK = dfK.drop('转换比N', axis=1, errors='ignore')
	dfK = dfK.rename(columns={'转换比M': '转换比N'})
	print('修正异常转换比产品', len(dfL), '条')
	print('异常单价记录转换比清洗完成')
	return dfK


def 修正价格异常(dfA):
	print('开始修正异常的单位价格记录....')
	dfB = dfA[['生产企业N', '成分名', '剂型N', '规格N', '单位价格']]
	dfC = dfB.groupby(['生产企业N', '成分名', '剂型N', '规格N']).median()
	dfC = dfC.reset_index()
	dfC = dfC.rename(columns={'单位价格': '价格中值'})
	dfA = pd.merge(dfA, dfC, how='left')
	dfA['异常指标'] = dfA['单位价格'] / dfA['价格中值']
	print('修正异常的单位价格记录', len(dfA.loc[(dfA['异常指标'] > 5) | (dfA['异常指标'] < 0.2)]), '条')
	dfA.loc[(dfA['异常指标'] > 5) | (dfA['异常指标'] < 0.2), '单位价格'] = np.nan
	dfA = dfA.drop(['异常指标', '价格中值'], axis=1, errors='ignore')
	return dfA


def 补充缺失价格(dfA):
	print('补充缺失价格...')
	dfB = dfA.groupby(['生产企业N', '成分名', '剂型N', '规格N']).median()['单位价格'].reset_index()
	dfB = dfB.rename(columns={'单位价格': '单位价格2'})
	dfA['价格标识'] = 0
	dfA.loc[pd.isnull(dfA['单位价格']), '价格标识'] = 1
	dfA = pd.merge(dfA, dfB, how='left')
	dfA['单位价格'] = dfA['单位价格'].fillna(dfA['单位价格2'])
	dfA = dfA.drop('单位价格2', axis=1, errors='ignore')
	print('补充缺失价格完成')
	return dfA


def 其他调整(dfA):
	print('还有一些其他调整需要完成')
	dfM = pd.read_excel(r'E:\我的招标项目数据\汇总工作表\价格状态更新\价格状态更新.xlsx')
	dfA = pd.merge(dfA, dfM, on='价格状态', how='left')
	dfA['价格状态更新'] = dfA['价格状态更新'].fillna(dfA['价格状态'])
	dfA = dfA.drop('价格状态', axis=1, errors='ignore')
	dfA = dfA.rename(columns={'价格状态更新': '价格状态'})
	dfB = dfA[['项目名称', '发布时间', '文件名', '成分名', '地区', '价格状态']]
	dfB = dfB.drop_duplicates()
	dfC = pd.merge(dfB.reset_index(), dfB.reset_index(), on=['地区', '成分名'], how='left')
	dfC = dfC.set_index(['index_x', 'index_y'])
	dfC = dfC.loc[dfC['文件名_x'] != dfC['文件名_y']].loc[
		(pd.to_datetime(dfC['发布时间_y']) - pd.to_datetime(dfC['发布时间_x'])) > timedelta(days=10)]
	dfE = dfC.groupby(level=0).apply(lambda dfout: dfout.sort_values(by='发布时间_y')[:1])
	dfE.index = dfE.index.droplevel(0)
	# dfC1 = dfC.loc[dfC['价格状态_y'].str.contains('国家') == 0]
	# dfE1 = dfC1.groupby(level=0).apply(lambda dfout: dfout.sort_values(by='发布时间_y')[:1])
	# dfF1 = dfE1[['文件名_x', '发布时间_y']]
	# dfF1 = dfF1.groupby('文件名_x').apply(lambda x: x['发布时间_y'].max()).reset_index()
	dfE = dfE[['项目名称_x', '发布时间_x', '文件名_x', '成分名', '发布时间_y']]
	dfG = dfE.groupby(['项目名称_x', '发布时间_x', '文件名_x', '成分名']).apply(lambda x: max(x['发布时间_y'])).reset_index()
	dfG = dfG.rename(columns={'项目名称_x': '项目名称', '发布时间_x': '发布时间', 0: '失效时间', '文件名_x': '文件名'})
	dfAA = pd.merge(dfA, dfG, how='left')
	# dfF1 = dfF1.rename(columns={'文件名_x': '文件名', 0: '失效时间2'})
	# dfAA = pd.merge(dfAA, dfF1, how='left')
	# dfAA['失效时间'] = dfAA['失效时间'].fillna(dfAA['失效时间2'])
	dfAA['失效时间'] = dfAA['失效时间'].fillna('2017-12-31')
	# dfAA = dfAA.drop('失效时间2', axis=1, errors='ignore')
	dfAA.loc[(dfAA['成分名'] == '人免疫球蛋白') & (dfAA['通用名'].str.contains('ph4', case=False)), '成分名'] = '人免疫球蛋白PH4'
	dfAA.loc[dfAA['商品名'] == '力扑素', '成分名'] = '紫杉醇脂质体'
	dfAA.loc[dfAA['成分名'] == '紫杉醇(白蛋白结合型)', '商品名'] = 'Abraxane'
	dfAA.loc[dfAA['成分名'] == '紫杉醇(白蛋白结合型)', '生产企业N'] = '赛尔基因生物制药'
	print('其他调整完成...等待结果输出')
	return dfAA

dfA = pd.read_csv(待合并文件1地址)  # 待合并文件1
dfB = pd.read_csv(待合并文件2地址)  # 待合并文件2
dfC = 文件合并(dfA, dfB)  # 文件合并
企业名称匹配(dfC)  # 企业名称匹配
dfC = 企业名称清洗(dfC, 待审核企业异名地址)  # 企业名称清洗
药品名称匹配(dfC)  # 药品名称匹配
dfC = 药品名称清洗(dfC, 待审核产品异名地址)  # 药品名称清洗

# dfC = 药品剂型规格清洗(dfC, 已上市药品规格地址)  # 药品剂型规格清洗
# dfC = 转换比清洗(dfC)  # 转换比清洗
# dfC = 单位价格清洗(dfC)# 单位价格清洗
# dfAA = 发现价格异常(dfC)#第一次发现价格异常
# dfC = 根据异常价格清洗转换比(dfC,dfAA)
# dfC = 单位价格清洗(dfC)# 修正转换比后再次单位价格清洗
# dfC = 修正价格异常(dfC)# 修正异常价格
# dfC = 商品名清洗(dfC)  # 商品名清洗
# dfC = 同商品名企业名称修正(dfC)
# dfC = 补充缺失价格(dfC)
# dfC = 其他调整(dfC)
# dfC.to_csv(r'E:\我的招标项目数据\汇总工作表\汇总测试.csv', index=False, encoding='utf-8')  # 文件输出
# print('全部结果输出至：E:\我的招标项目数据\汇总工作表\汇总测试.csv')
# dfA = dfA.drop(['预留字段1', '预留字段2', '预留字段3'], axis=1, errors='ignore')
# dfA['flag2'] = 1
# dfM = pd.merge(dfC, dfA, how='left')
# dfM = dfM.loc[pd.isnull(dfM['flag2'])]
# dfM = dfM.drop(['flag2'], axis=1, errors='ignore')
# dfM.to_csv(r'E:\我的招标项目数据\汇总工作表\增量更新.csv', index=False, encoding='utf-8')  # 文件输出
# print('增量结果输出至：E:\我的招标项目数据\汇总工作表\增量更新.csv')
# print('Done！')
