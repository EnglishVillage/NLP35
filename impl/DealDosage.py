#!/usr/bin/python3.5
# -*- coding:utf-8 -*-

import os, sys, re, time

sys.path.append("/home/esuser/NLP35")
import numpy as np
import pandas as pd
from flask import Flask, jsonify, abort, make_response, request
from utils import StringUtils

app = Flask(__name__)


# 400页面
@app.errorhandler(400)
def not_found(error):
	return make_response(jsonify({"error": "没有接收到可用数据!(No data was received!)"}), 404)


@app.route("/")
def index():
	return "Hello, World!"


@app.route("/python/api/deal/dosage", methods=["POST"])
def deal_dosage():
	# 使用Body中的x-www.form.urlencoded进行发送
	if len(request.values) < 1:
		abort(400)
	# 多个剂型组成的字符串,分割符为@@
	text = request.values["text"]
	result = deal_dosage_core(text, None)
	return jsonify({"result": result}), 200


params1 = {"０": "0", "１": "1", "２": "2", "３": "3", "４": "4", "５": "5", "６": "6", "７": "7", "８": "8", "９": "9", "Ａ": "A", "Ｂ": "B", "Ｃ": "C", "Ｄ": "D", "Ｅ": "E", "Ｆ": "F", "Ｇ": "G", "Ｈ": "H", "Ｉ": "I", "Ｊ": "J", "Ｋ": "K", "Ｌ": "L", "Ｍ": "M", "Ｎ": "N", "Ｏ": "O", "Ｐ": "P", "Ｑ": "Q", "Ｒ": "R", "Ｓ": "S", "Ｔ": "T", "Ｕ": "U", "Ｖ": "V", "Ｗ": "W", "Ｘ": "X", "Ｙ": "Y", "Ｚ": "Z", "ａ": "a", "ｂ": "b", "ｃ": "c", "ｄ": "d", "ｅ": "e", "ｆ": "f", "ｇ": "g", "ｈ": "h", "ｉ": "i", "ｊ": "j", "ｋ": "k", "ｌ": "l", "ｍ": "m", "ｎ": "n", "ｏ": "o", "ｐ": "p", "ｑ": "q", "ｒ": "r", "ｓ": "s", "ｔ": "t", "ｕ": "u", "ｖ": "v", "ｗ": "w", "ｘ": "x", "ｙ": "y", "ｚ": "z"}
params2 = {"毫": "m", "升": "l", "克": "g", "axa": "", "抗": "", "国际单位": "iu", "单位": "iu", "微": "u", "Μ": "u", "μ": "u", "：": ":", "（": "("}
params3 = {"十万": 100000, "百万": 1000000, "千万": 10000000, "十亿": 1000000000, "百亿": 10000000000, "千亿": 100000000000, "万亿": 1000000000000}
params4 = {"十": 10, "百": 100, "千": 1000, "万": 10000, "亿": 100000000}


# 每揿含沙丁胺醇0.14mg
p_g = r"[0-9]+\.?[0-9]*[十百千万亿]*[kmu]?[g揿]"
p_l = r"[0-9]+\.?[0-9]*[十百千万亿]*[mu]?l"
p_i = r"[0-9]+\.?[0-9]*[十百千万亿]*[w]?iu"
p_per = r"[0-9]+\.?[0-9]*(?=%)"
p_g_times = r"每([0-9]+\.?[0-9]*)?(揿含)?.*"


# p_per2 = r"[0-9]+\.?[0-9]+$"


# 预处理替换函数
def prefix(ps, parmas):
	if ps:
		ps = ps.strip().lower()
		ps = StringUtils.replace_key(ps, parmas)
	return ps


def add_val_core(value, result, unit, myformat):
	result.append(myformat.format(format(value, ".2f").replace(".00", ""), unit))


def add_val(value, result, unit, s_sub):
	if "(" in s_sub:
		add_val_core(value, result, unit, "({}{})")
	else:
		if "与" in s_sub or "含" in s_sub or ":" in s_sub:
			add_val_core(value, result, unit, ":{}{}")
		else:
			add_val_core(value, result, unit, "{}{}")


def add_value_per(val, result, unit, nums, s_sub):
	# 除以每XXX
	if nums:
		if nums[0][0]:
			val = val / float(nums[0][0])
		if "揿含" == nums[0][1]:
			unit = unit + "/揿"
		add_val(val, result, unit, s_sub)


def add_g(value, result, s_sub, v, pattern, unit):
	# 获取每XXX後面的数量
	search = re.search(pattern, s_sub)
	if search:
		# 得到匹配到的字符串
		match = search.group()
		s_sub = s_sub.replace(match, "")
		nums = re.findall(pattern, match)
		add_value_per(value, result, unit, nums, s_sub)
		# 可能有包含每XXX,也有不包含每XXX
		if v in s_sub:
			add_val(value, result, unit, s_sub)
	else:
		add_val(value, result, unit, s_sub)


# 获取各个值所对应的范围
def get_out_index(out, s):
	out_index = []
	begin = 0
	for v in out:
		end = s[begin:].index(v) + len(v) + begin
		out_index.append((begin, end))
		begin = end
	return out_index


def get_out_ls(result):
	ls = []
	for s in result:
		if s not in ls:
			if ":" in s:
				if ls:
					if ")" in ls[-1]:
						ls[-1] = ls[-1][:-1] + s + ")"
					else:
						ls[-1] = ls[-1] + s
				else:
					ls.append(s[1:])
			elif "(" in s:
				if ls:
					ls[-1] = ls[-1] + s
				else:
					ls.append(s)
			else:
				ls.append(s)
	return ls


# 将字符串类型数字转化为数字,并替换中文倍数
def replace_unit(value, multiple=1):
	try:
		flag = True
		for k, v in params3.items():
			if k in value:
				value = float(value.replace(k, "")) * v
				flag = False
				break
		if flag:
			for k, v in params4.items():
				if k in value:
					value = float(value.replace(k, "")) * v
					flag = False
					break
		if flag:
			value = float(value)
		value *= multiple
	except:
		value = None
	return value


def get_unit_and_value_g(val):
	if "揿" in val:
		unit = "揿"
		value = val.rstrip("揿")
		value = replace_unit(value)
	else:
		unit = "mg"
		if "mg" in val:
			value = val.rstrip("mg")
			value = replace_unit(value)
		elif "ug" in val:
			# ug 转化为 mg
			value = val.rstrip("ug")
			value = replace_unit(value, 1 / 1000)
		else:
			# g 转化为 mg
			value = val.rstrip("g")
			value = replace_unit(value, 1000)
	return (unit, value)


def get_unit_and_value_l(val):
	unit = "ml"
	# 获取值
	if "ml" in val:
		value = val.rstrip("ml")
		value = replace_unit(value)
	elif "ul" in val:
		value = val.rstrip("ul")
		value = replace_unit(value, 1 / 1000)
	else:
		value = val.rstrip("l")
		value = replace_unit(value, 1000)
	return (unit, value)


def get_unit_and_value_iu(val):
	unit = "iu"
	# 获取值
	if "wiu" in val:
		value = val.rstrip("wiu")
		value = replace_unit(value, 10000)
	else:
		value = val.rstrip("iu")
		value = replace_unit(value)
	return (unit, value)


def get_unit_and_value_per(val):
	return ("%", replace_unit(val))


def specification_extraction_core(result, sou, p_g, get_unit_and_value_func):
	match = re.findall("\(.*?\)", sou)
	ls_sou = []
	if match:
		begin = 0
		for m in match:
			index = sou.index(m, begin)
			if begin < index:
				ls_sou.append(sou[begin:index])
			ls_sou.append(m)
			begin = index + len(m)
		if begin < len(sou):
			ls_sou.append(sou[begin:])
	else:
		ls_sou.append(sou)
	for s in ls_sou:
		# 获取值
		out = re.findall(p_g, s)
		# 获取值所对应的范围
		out_index = get_out_index(out, s)
		flag = False
		last_t = None
		for i, v in enumerate(out):
			if flag:
				flag = False
				if last_t[1] == out_index[i][0]:
					s_sub = s[last_t[0]:out_index[i][1]]
				else:
					s_sub = s[out_index[i][0]:out_index[i][1]]
			else:
				s_sub = s[out_index[i][0]:out_index[i][1]]
			# 判断是否含有:每2揿,每2mg,如果有则保存起來,作为下次使用
			if "每" + v in s_sub:
				flag = True
				last_t = out_index[i]
				continue
			# 获取单位和清洗後的值
			t = get_unit_and_value_func(v)
			if t[1]:
				add_g(t[1], result, s_sub, v, p_g_times + v, t[0])
	return get_out_ls(result)


# 规格提取
def specification_extraction(s, flag=1):
	# flag = 1 提取全部剂型，flag =2 只提取mg，flag=3 只提取ml flag=4 只提取IU flag=5 只提取百分比
	result = []
	if flag == 2:
		result = specification_extraction_core(result, s, p_g, get_unit_and_value_g)
		return " ".join(result)
	elif flag == 3:
		result = specification_extraction_core(result, s, p_l, get_unit_and_value_l)
		return " ".join(result)
	elif flag == 4:
		result = specification_extraction_core(result, s, p_i, get_unit_and_value_iu)
		return " ".join(result)
	elif flag == 5:
		result = specification_extraction_core(result, s, p_per, get_unit_and_value_per)
		out4 = re.findall(p_g, s)
		out5 = re.findall(p_l, s)
		for m in out5:  # 将mg ml转换为%比浓度
			# 获取毫升
			t = get_unit_and_value_l(m)
			k = t[1]
			for val in out4:
				t2 = get_unit_and_value_g(val)
				value = t2[1]
				# 计算百分比
				if k:
					value = value / (k * 10)
				else:
					value = 0
				add_val(value, result, "%", "")
		return " ".join(get_out_ls(result))
	return " ".join(result)


def get_value(row, ls, field):
	newmg = [w for w in row[field].split()]
	if newmg:
		ls.append(";".join(newmg))


def deal_dosage_core(text, other=None):
	df = pd.DataFrame(pd.Series(text.split("@@")), columns=("dosage",))
	df["dosage"] = df["dosage"].astype(str)
	df["dosage2"] = df["dosage"].apply(prefix, args=(params1,))
	df["dosage2"] = df["dosage2"].apply(prefix, args=(params2,))
	df["dosage_mg"] = df["dosage2"].apply(specification_extraction, args=(2,))
	df["dosage_ml"] = df["dosage2"].apply(specification_extraction, args=(3,))
	df["dosage_iu"] = df["dosage2"].apply(specification_extraction, args=(4,))
	df["dosage_per"] = df["dosage2"].apply(specification_extraction, args=(5,))
	result = []
	ls = []
	for ix, row in df.iterrows():
		ls.clear()
		get_value(row, ls, "dosage_mg")
		get_value(row, ls, "dosage_ml")
		get_value(row, ls, "dosage_iu")
		get_value(row, ls, "dosage_per")
		result.append((row["dosage"], ",".join(ls).replace("(", "").replace(")", "")))
	return result


if __name__ == '__main__':
	# aa=deal_dosage_core("(1)每支20ml (2)每瓶装200ml@@(1)每支装10ml (2)每瓶装200ml@@250ml:12.5g(总氨基酸)")
	# aa = deal_dosage_core("(1)每10支20g;每支20g,每20支20g@@(2)每2瓶装200.2mg@@(1)每支装10.ug (2)每3瓶装200ug@@250ml:12.5g(总氨基酸)")
	# aa = deal_dosage_core("(1)每10支20g@@每支20g@@每20支20g@@每10支20g")
	# aa = deal_dosage_core("(1)每10支20g;每支20g,每20支20g每10支20g")
	# aa = deal_dosage_core("每袋装５万揿,每10袋装５万揿,每袋装５千揿每袋装５揿每袋装５万mｇ,每10袋装５万mｇ,每袋装５千mｇ每袋装５mｇ")
	# aa = deal_dosage_core("每袋装５万mｇ,每10袋装５万mｇ,每袋装５千mｇ每袋装５mｇ")
	# aa = deal_dosage_core("每瓶装6mg、10mg、25mg")
	# aa = deal_dosage_core("每瓶300mg,每2揿含沙丁胺醇14万mg,每瓶200揿,每揿含沙丁胺醇0.14mg")
	# aa = deal_dosage_core("每瓶14g,含沙丁胺醇20mg,药液浓度为0.14%(g/g),每揿含沙丁胺醇0.10mg")
	# aa = deal_dosage_core("3.0g(头孢哌酮1.5g:舒巴坦1.5g)")
	# aa = deal_dosage_core("aaa12.5万阿奇霉素单位)")
	# print(aa)

	# bb = deal_dosage_core("(1)每10支20l;每支20l,每20支20l@@(2)每2瓶装200.2ml@@(1)每支装10.ul (2)每3瓶装200ul@@250ml:12.5l(总氨基酸)")
	# print(bb)
	# bb = deal_dosage_core("(1)每10支20l@@每支20l@@每20支20l@@每10支20l")
	# print(bb)
	# bb = deal_dosage_core("(1)每10支20l;每支20l,每20支20l每10支20l")
	# print(bb)
	# bb = deal_dosage_core("每瓶300ml,(每2揿含沙丁胺醇14万ml),每瓶200揿,(每揿含沙丁胺醇0.14ml)")
	# bb = deal_dosage_core("药液浓度为0.2%(g/g)革夺村32ml:52mg工")
	# print(bb)

	app.run(host='0.0.0.0', port=5003, debug=True)
	print("over")
