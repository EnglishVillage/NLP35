#!/usr/bin/python
# -*- coding:utf-8 -*-


"""
参考:http://www.cnblogs.com/skying555/p/6541612.html
原版代码：https://github.com/cleverdeng/pinyin.py

新增功能：
	1、可以传入参数firstcode：如果为true，只取汉子的第一个拼音字母；如果为false，则会输出全部拼音；
	2、修复：如果为英文字母，则直接输出；
	3、修复：如果分隔符为空字符串，仍然能正常输出；
	4、升级：可以指定词典的文件路径
"""

import os, sys, re, time
import requests
from pypinyin import pinyin, lazy_pinyin
import pypinyin

class PinYin(object):
	def __init__(self):
		self.word_dict = {}

	def load_word(self, dict_file):
		self.dict_file = dict_file
		if not os.path.exists(self.dict_file):
			raise IOError("NotFoundFile")
		with open(self.dict_file, "r", encoding="utf-8") as f:
			for line in f.readlines():
				line = line.split('|')
				try:
					self.word_dict[line[0]] = line[1]
				except:
					print(line)

	def hanzi2pinyin(self, string="", firstcode=False):
		result = []
		if not isinstance(string,str):
			string = str(string)
		for char in string:
			key = '%X' % ord(char)
			value = self.word_dict.get(key, char)
			outpinyin = str(value).split()[0][:-1].lower()
			if not outpinyin:
				outpinyin = char
			if firstcode:
				result.append(outpinyin[0])
			else:
				result.append(outpinyin)
		return result

	def hanzi2pinyin_split(self, string="", split="", firstcode=False):
		"""提取中文的拼音
		@param string:要提取的中文
		@param split:分隔符
		@param firstcode: 提取的是全拼还是首字母？如果为true表示提取首字母，默认为False提取全拼
		"""
		result = self.hanzi2pinyin(string=string, firstcode=firstcode)
		return split.join(result)
	
def pinyin2hanzi(pinyin="pinyin"):
	"""
	调用baidu相关API将拼音转化为汉字
	:param pinyin:
	:return:
	"""
	base_url = "http://olime.baidu.com/py"
	playload = {
		"input":pinyin,
		"inputtype":"py",
		"bg":0,
		"ed":1,
		"result":"hanzi",
		"resultcoding":"unicode",
		"ch_en":0,
		"clientinfo":"web",
		"version":1
	}
	json_data = requests.get(base_url,params=playload).json()
	return json_data["result"][0][0][0]

# test = PinYin()
# test.load_word(os.path.join("..", "sources", "pingyin.data"))
# string = "Java程序性能优化-让你的Java程序更快更稳定"
# string = "阿莫西林"
# print("in: %s" % string)
# print("out: %s" % str(test.hanzi2pinyin(string=string)))
# print("out: %s" % test.hanzi2pinyin_split(string=string, split="", firstcode=True))
# print("out: %s" % test.hanzi2pinyin_split(string=string, split="", firstcode=False))

# result=pinyin2hanzi("阿莫西林")
# print(result)



# print(pinyin('中心',style=pypinyin.NORMAL, heteronym=True))
# list=pinyin('重组人凝血因子viii融合蛋白',style=pypinyin.NORMAL, heteronym=True)

# list=pypinyin.slug('重组人凝血因子viii融合蛋白',separator="")
# print(list)
# list=[['zhong'], ['xin']]
# print([y for x in list for y in x])


# print(pypinyin.slug('阿莫呈西林中心',separator=""))
# print(pypinyin.slug('阿莫西林中心',separator="",style=pypinyin.FIRST_LETTER))





