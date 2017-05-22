#!/usr/bin/python
# -*- coding:utf-8 -*-

import Levenshtein

# # 返回编辑操作顺序(这个看不懂...)
# e = Levenshtein.editops('spam', 'park')
# print(e)
# e = Levenshtein.editops('man', 'scotsman')
# print(e)
# result=Levenshtein.apply_edit(e, 'man', 'scotsman')
# print(result)
# result=Levenshtein.apply_edit(e[:3], 'man', 'scotsman')
# print(result)
#
# a, b = 'spam and eggs', 'foo and bar'
# e = Levenshtein.opcodes(a, b)
# print(e)
# # 反转编辑操作顺序
# result= Levenshtein.apply_edit(Levenshtein.inverse(e), b, a)
# print(result)
# e[4] = ('equal', 10, 13, 8, 11)
# print(e)
# result= Levenshtein.apply_edit(e, a, b)
# print(result)


str1 = "biologics"
str2 = "biologisc"
str1="书包"
str2="背包"
# 汉明距离【越小越好】(两个字符串对应位置的不同字符的个数):2个字符串长度必须相同,区分大小写
length=Levenshtein.hamming(str1, str2)
print(length)
# 编辑距离【越小越好】(由一个转成另一个所需的最少编辑操作(增删改)次数):区分大小写
length=Levenshtein.distance(str1, str2)
print(length)
# 莱文斯坦比【越大越好】(r =(sum-ldist)/sum,sum是指str1和str2长度总和,ldist是类编辑距离[类编辑距离:删除、插入依然+1，但是替换+2])
length=Levenshtein.ratio(str1, str2)
print(length)


# Jaro算法【越大越好】(dj=(m/len1+m/len2+(m-t)/m)/3,m是2个字符串相同的字符个数,len是字符串长度,t是换位数目)
length=Levenshtein.jaro('Brian', 'Jesus')
print(length)
length=Levenshtein.jaro('Thorkel', 'Thorgier')  # doctest: +ELLIPSIS
print(length)
length=Levenshtein.jaro('Dinsdale', 'D')  # doctest: +ELLIPSIS
print(length)
print("\n")
# jaro_winkler算法【越大越好】(dw=dj+(l*p*(1-dj)),dj是jaro值,l是相同前缀长度,p是权重(默认0.1,不超过0.25)),给公共前缀赋予更多的权重
length=Levenshtein.jaro_winkler('Brian', 'Jesus')
print(length)
length=Levenshtein.jaro_winkler('Thorkel', 'Thorgier')  # doctest: +ELLIPSIS
print(length)
length=Levenshtein.jaro_winkler('Dinsdale', 'D')  # doctest: +ELLIPSIS
print(length)
length=Levenshtein.jaro_winkler('pharma', 'pharmaceuticals', 0.12)
print(length)