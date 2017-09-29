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


