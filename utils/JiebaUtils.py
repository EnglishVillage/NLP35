#!/usr/bin/python3.5
# -*- coding:utf-8 -*-

import sys
# sys.path.append("../")
import jieba

# 自定义的词库的词频和类型
from utils import IOUtils

freqandtag = "@@3@@nz"

def writefile(path: str, ls,freqandtag = "@@3@@nz"):
	if ls:
		# 写入到文件中
		with open(path, "w", encoding="utf-8") as f:
			if isinstance(ls,list):
				tagList=ls
			else:
				tagList = list(ls)
			tagList.sort(key=lambda str: len(str), reverse=False)
			length = len(tagList) - 1
			# 这里只遍历N-1个元素,因为每页有加换行符
			for i in range(length):
				f.write(tagList[i] + freqandtag + "\n")
			# 最後一个没有换行符
			f.write(tagList[length] + freqandtag)

def wkztest():
	text = ("李小福是创新办主任也是云计算方面的专家; 什么是八一双鹿\n"
				 "例如我输入一个带“韩玉赏鉴”的标题，Edu Trust认证在自定义词库中也增加了此词为N类\n"
				 "「台中」正確應該不會被切開。mac上可分出「石墨烯」；此時又可以分出來凱特琳了。")

	# jieba.load_userdict(IOUtils.get_path_sources("userdict.txt"))
	# jieba.add_word('石墨烯')
	# jieba.add_word('凱特琳')
	# jieba.del_word('自定义词')


	# words = jieba.cut(text)
	# print(words)
	# print('/'.join(words))

	# print("=" * 40)
	#
	# result = pseg.cut(text)
	#
	# for w in result:
	# 	print(w.word, "/", w.flag, ", ", end=' ')
	#
	# print("\n" + "=" * 40)
	#
	# terms = jieba.cut('easy_install is great')
	# print('/'.join(terms))
	# terms = jieba.cut('python 的正则表达式是好用的')
	# print('/'.join(terms))
	#
	# print("=" * 40)
	# # test frequency tune
	# testlist = [('今天天气不错', ('今天', '天气')), ('如果放到post中将出错。', ('中', '将')), ('我们中出了一个叛徒', ('中', '出')), ]
	#
	# for sent, seg in testlist:
	# 	print('/'.join(jieba.cut(sent, HMM=False)))
	# 	word = ''.join(seg)
	# 	print('%s Before: %s, After: %s' % (word, jieba.get_FREQ(word), jieba.suggest_freq(seg, True)))
	# 	print('/'.join(jieba.cut(sent, HMM=False)))
	# 	print("-" * 40)

	tokenizer_all = jieba.Tokenizer(IOUtils.get_path_sources("userdict.txt"))
	result=tokenizer_all.cutwkz_dict(text)
	# result=tokenizer_all.cutwkz_dict(text)
	print(result)

# wkztest()