#!/usr/bin/python3.5
# -*- coding:utf-8 -*-

import os, sys, re, time

sys.path.append('/home/esuser/NLP35')
import Levenshtein
import jieba
from bs4 import BeautifulSoup
from flask import Flask, jsonify, abort, make_response, request
from impl2 import MatchCore
from impl2.MatchCore import MatchType
from utils import OtherUtils, IOUtils, CollectionUtils, RegexUtils, JiebaUtils, StringUtils

app = Flask(__name__)


# 400页面
@app.errorhandler(400)
def not_found(error):
	return make_response(jsonify({'error': '没有接收到可用数据!(No data was received!)'}), 404)


@app.route("/")
def index():
	return "Hello, World!"


@app.route('/python/api/match/company', methods=['POST'])
def match_company():
	# 使用Body中的x-www.form.urlencoded进行发送
	if len(request.values) < 1:
		abort(400)
	text = request.values["text"]
	fields = request.values["fields"]
	isfields = 1
	if "isfields" in request.values:
		isfields = None
	result = match_core(text, fields, 1, isfields)
	return jsonify(result), 200


@app.route('/python/api/match/drug', methods=['POST'])
def match_drug():
	# 使用Body中的x-www.form.urlencoded进行发送
	if len(request.values) < 1:
		abort(400)
	text = request.values["text"]
	fields = request.values["fields"]
	result = match_core(text, fields, 2, None)
	return jsonify(result), 200


# 精确匹配字段和模糊匹配字段
match_fields_exact_company = {"business_anonymous", "short_name", "short_name_en", "name", "name_en"}
match_fields_fuzzy_company = {"name_used", "all_name"}
# 查询字段
fields_company = "id,code,name,capital_name,name_en,name_used,business_anonymous,short_name,short_name_en,registered_type,registered_country,qichacha_link,is_important_corp,official_website,address,stock,parent_company,create_time,modify_time,state,remark,logo,all_name,weixin"
fieldlist_company = fields_company.split(",")
# 精确匹配字段和模糊匹配字段对应的角标
match_index_exact_company = {fieldlist_company.index(i) for i in match_fields_exact_company}
match_index_fuzzy_company = {fieldlist_company.index(i) for i in match_fields_fuzzy_company}
sql_company = "select " + fields_company + " from base_company where is_delete = '否'"

# 精确匹配字段和模糊匹配字段
match_fields_exact_drug = {"name_original", "name_short_en", "name_original_en", "name_short", "name", "name_en"}
match_fields_fuzzy_drug = {"name_anonymous", "name_synonyms", "all_name"}
# 查询字段
fields_drug = "id,code,name,name_en,name_synonyms,name_anonymous,rd_code,name_original,name_original_en,is_important_drug,is_combination,drug_type,formulation,search_formulation,department,indication,create_time,modify_time,state,all_name,inn_id,name_short,name_short_en"
fieldlist_drug = fields_drug.split(",")
# 精确匹配字段和模糊匹配字段对应的角标
match_index_exact_drug = {fieldlist_drug.index(i) for i in match_fields_exact_drug}
match_index_fuzzy_drug = {fieldlist_drug.index(i) for i in match_fields_fuzzy_drug}
sql_drug = "select " + fields_drug + " from base_drug "
# 字典
dict_company = None
dict_drug = None
keys_company = None
keys_drug = None
# 分词器
tokenizer_company = None
tokenizer_drug = None
# jaro_winkler算法的前缀权重
bound = 0.14

replace_dict_fuzzy_company = {'省': '', '市': '', '股份有限公司': '', '有限公司': '', '有限责任公司': '', '经济特区': '', '广西壮族自治区': '广西', '西藏自治区': '西藏', '宁夏回族自治区': '宁夏', '内蒙古自治区': '内蒙古', '新疆维吾尔自治区': '新疆', '宁夏回族自治区': '宁夏', '阿坝藏族羌族自治区': '阿坝', '生产企业': '', '委托方': '', '葯': '药', '零': '0', '一': '1', '二': '2', '三': '3', '四': '4', '五': '5', '六': '6', '七': '7', '八': '8', '九': '9', '委托方': '', '会社': ''}  # 企业名称清洗预处理字典
replace_dict_fuzzy_drug = {"铵": "胺", "苯": "本", "比": "吡", "宾": "滨", "哒": "达", "喋": "蝶", "汀": "丁", "啶": "定", "双": "二", "夫": "福", "已": "己", "力": "立", "啉": "林", "吟": "呤", "卢": "芦", "伦": "仑", "罗": "洛", "脒": "咪", "拉": "那", "內": "内", "粘": "黏", "派": "哌", "朴": "扑", "秦": "嗪", "脱": "去", "斯": "司", "西": "昔", "性": "型", "依": "伊", "黏": "粘", "征": "症", "脂": "酯", "呋": "福", "米": "咪", "思": "司", "衣": "伊", "证": "症", "前列": "前", "右旋": "右", "左旋": "左"}
swap_company1 = r'(^中国|爱尔兰|阿根廷|澳大利亚|巴西|生产厂|列支敦士登|美国|韩国|意大利|法国|无|德国|英国|日本|西班牙|比利时|印度|加拿大|希腊|荷兰|波多黎各|墨西哥|新加坡|台湾|波兰|丹麦|瑞典|瑞士|冰岛)(\S+)'
swap_company2 = r'(山西|内蒙古|河北|安徽|4川|湖北|云南|天津|江西|江苏|浙江|湖南|吉林|黑龙江|辽宁|上海|贵州|陕西|甘肃|广东|河南|新疆|山东|海南|北京|福建|宁夏|青海|军区|广西|重庆|西藏)(\S+)'
re_swap_company1 = re.compile(swap_company1)
re_swap_company2 = re.compile(swap_company2)
re_swap_drug = re.compile(r'(^\S+酸)(\S+)')


def replace_key_drug(key):
	"""
	药品替换错别字
	:param key:
	:return:
	"""
	return StringUtils.replace_key(key, replace_dict_fuzzy_drug)


def replace_key_company(key):
	return StringUtils.replace_key(key, replace_dict_fuzzy_company)


def diy_drug(key):
	key = replace_key_drug(key)
	key = re_swap_drug.sub(r'\2\1', key)
	return key


def diy_company(key):
	key = replace_key_company(key)
	key = re_swap_company1.sub(r'\2\1', key)
	key = re_swap_company2.sub(r'\2\1', key)
	return key


def predeal(key):
	"""
	对key进行通用处理
	:param key:
	:return:
	"""
	key = key.replace("（", "(").replace("）", ")").replace("【", "[").replace("】", "]")
	key = RegexUtils.replace_diy_chars(key, "\(.*?\)")
	newkey = RegexUtils.replace_diy_chars(key, "\[.*?\]")
	if newkey:
		key = newkey
	key = key.replace("〇", "0")
	key = RegexUtils.get_word_nospecial(key)
	key = key.lower().strip()
	return key


#################################

def match_exact(row, dict_all, model, match_index_exact, extra_func=None):
	for i in match_index_exact:
		key = row[i]
		if key:
			key = predeal(key)
			if extra_func:
				key = extra_func(key)
			if key:
				dict_all[key] = model


def match_fuzzy(row, dict_all, model, match_index_fuzzy, extra_func=None):
	for i in match_index_fuzzy:
		field = row[i]
		if field:
			keys = field.split("|")
			for key in keys:
				if key:
					key = predeal(key)
					dict_all[key] = model


def match_exact_company(row, dict_all, model, match_index_exact):
	match_exact(row, dict_all, model, match_index_exact, diy_company)


def match_exact_drug(row, dict_all, model, match_index_exact):
	match_exact(row, dict_all, model, match_index_exact, diy_drug)


def match_fuzzy_company(row, dict_all, model, match_index_fuzzy):
	match_fuzzy(row, dict_all, model, match_index_fuzzy, diy_company)


def match_fuzzy_drug(row, dict_all, model, match_index_fuzzy):
	match_fuzzy(row, dict_all, model, match_index_fuzzy, diy_drug)


def set_result_model(mydict, key, winkler, values_set, fields, similarity_field):
	model = mydict[key]
	for field in fields:
		if field == similarity_field:
			values_set[similarity_field] = "{0}%".format(int(winkler * 100))
		else:
			values_set[field] = model[field]


def match_model(txt, fields, keys, mydict, similarity_field):
	flag = True
	values_set = {}
	winkler_map = {}
	for key in keys:
		# 越大越好
		winkler = Levenshtein.jaro_winkler(txt, key, bound)
		if winkler == 1.0:
			flag = False
			set_result_model(mydict, key, winkler, values_set, fields, similarity_field)
			break
		elif winkler > 0.7:
			CollectionUtils.add_dict_setvalue_single(winkler_map, winkler, key)
	if flag:
		if winkler_map:
			winkler = max(winkler_map.keys())
			keys_set = winkler_map[winkler]
			if len(keys_set) > 1:
				temp_map = {}
				for key in keys_set:
					# 越小越好
					distance = Levenshtein.distance(txt, key)
					CollectionUtils.add_dict_setvalue_single(temp_map, distance, key)
				distance = min(temp_map.keys())
				keys_set = temp_map[distance]
				if len(keys_set) > 1:
					temp_map.clear()
					for key in keys_set:
						CollectionUtils.add_dict_setvalue_single(temp_map, len(key), key)
					length = min(temp_map.keys())
					key = temp_map[length].pop()
				else:
					key = keys_set.pop()
				set_result_model(mydict, key, winkler, values_set, fields, similarity_field)
			else:
				key = keys_set.pop()
				set_result_model(mydict, key, winkler, values_set, fields, similarity_field)
		else:
			return None
	return values_set


def get_result_empty(fields):
	mapresult = {}
	for field in fields:
		mapresult[field] = ""
	return mapresult


def match_core(text, fields, putlabeltype, other=None):
	"""

	:param text:
	:param fields:
	:param putlabeltype: 1公司2药品
	:param other:
	:return:
	"""
	if fields:
		fields = fields.split("|")
		if fields:
			fields = {field for field in fields if field}
		else:
			return None
	else:
		return None
	if not text:
		return get_result_empty(fields)
	text = BeautifulSoup(text, "html.parser").get_text().replace("\n", "")
	# 去括号里面东西
	txt = text.replace("（", "(").replace("）", ")")
	txt = RegexUtils.replace_diy_chars(txt, "\(.*?\)")
	txt = RegexUtils.replace_diy_chars(txt, "\[.*?\]")
	txt = " ".join(txt.split()).lower()
	mapresult = None
	# 匹配公司
	if putlabeltype == 1:
		companys = txt.split(";")
		values_dict = {}
		for company in companys:
			if company:
				company = RegexUtils.replace_special_chars_nosplit(company)
				model = match_model(company, fields, keys_company, dict_company, "company_match_degree")
				if model:
					values_dict[str(model)] = model
		if values_dict:
			if other == 1:
				values = values_dict.values()
				for value in values:
					mapresult = value
					break
			else:
				mapresult = {}
				for value in values_dict.values():
					for key in value.keys():
						if key in mapresult:
							mapresult[key] = "{0}|{1}".format(mapresult[key], value[key])
						else:
							mapresult[key] = str(value[key])
	# 匹配药品
	elif putlabeltype == 2:
		txt = RegexUtils.replace_special_chars_nosplit(txt)
		mapresult = match_model(txt, fields, keys_drug, dict_drug, "drug_match_degree")
	if not mapresult:
		mapresult = get_result_empty(fields)
	return mapresult


if __name__ == '__main__':
	readcache = False

	dict_company, jieba_dict_company = MatchCore.writedict(MatchType.company, sql_company, fieldlist_company,
														   match_index_exact_company, match_index_fuzzy_company,
														   match_exact_company, match_fuzzy_company, iscache=readcache)

	dict_drug, jieba_dict_drug = MatchCore.writedict(MatchType.drug, sql_drug, fieldlist_drug, match_index_exact_drug,
													 match_index_fuzzy_drug, match_exact_drug, match_fuzzy_drug,
													 iscache=readcache)

	keys_company = dict_company.keys()
	keys_drug = dict_drug.keys()

	# result = match_key("华彬", "code|name|capital_name|name_en", 1)
	# result = match_key("胶", "code|name|name_en|name_synonyms|name_anonymous", 2)
	# print(result)

	# 本机只能通过127.0.0.1或者localhost可访问,其它机子只能通过192.168.2.135可以访问(默认是5000)
	app.run(host='0.0.0.0', port=5002, debug=True)

	# print(diy_drug("铵aaa胺bbb酸苯asdf本"))

	print("\nover")
