#!/usr/bin/python
# -*- coding:utf-8 -*-

# from __future__ import print_function, unicode_literals
import os
import sys
# sys.path.append("../")
import jieba
import jieba.posseg as pseg





# jieba默认分词器
# jieba.dt=jieba.Tokenizer()
# 添加自定义词典到默认分词器jieba.dt(词典:词语 词频（可省略） 词性（可省略）)
# jieba.load_userdict(os.path.join("..","sources","userdict.txt"))
# jieba.add_word()

#自定义分词器
# tokenizer = jieba.Tokenizer(dictionary=os.path.join("..","sources","userdict.txt"))
tokenizer = jieba.Tokenizer(dictionary=os.path.join("..","sources","createdict"))

test_sent = (
"李小福是创新办主任G蛋白偶联受体49也是补体因子H和云计算方面的专家; 什么是prostate stem cell antigen (psca)或者八一双鹿\n"
"例如我解旋酶-引物酶输入G蛋白偶联受体49一个带“韩玉赏鉴”的标题，Edu Trust认证在补体受体2自定义词库中成纤维细胞生长因子18也增加了此词为N类\n"
"「台中」正確钠离子通道Nav1.8應該不會wang kun zao被切開α5β1整合素。mac上可分出「石墨烯」；此時又可以分出來二磷酸尿核苷葡糖醛酸基转移酶1家族肽A1凱特琳了。\n"
"怎样Citroën growth可以强制insulin-like growth factor 1 receptor hi提高一些关键词中一些词果糖-1,6-二磷酸酶的权重呀血管紧张素(1-7)"
)
#
cut= tokenizer.cut(test_sent,False,False)
print("/".join(cut))



print(1)












