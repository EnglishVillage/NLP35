#!/usr/bin/python3.5
# -*- coding:utf-8 -*-
import os, sys, re, time

sys.path.append('/home/esuser/NLP35')
from enum import Enum
from elasticsearch2 import Elasticsearch


class QueryType(Enum):
	# 大于
	GT = 1
	# 小于
	LT = 2
	# 大于等于
	GE = 3
	# 小于等于
	LE = 4
	# 范围查询[左右都闭合](Between)
	BN = 5
	# 类似于sql中的not in关键字[都是Or的关系=值都是精确匹配]
	NI = 6
	# 类似于sql中的in关键字[都是Or的关系=值都是精确匹配]
	IN = 7
	# 类似于sql中的in关键字[都是Or的关系=但是值是模糊匹配]
	IN_LIKE = 8
	# 类似于sql模糊查询[不对查询字符串进行分词]
	NL = 9
	# 类似于sql模糊查询[不对查询字符串进行分词]
	LIKE = 10
	# 类似于sql模糊查询[对查询字符串进行分词]
	LIKE_ANALYSE = 11
	# 不相等
	NE = 12
	# 等于
	EQ = 14


class Query(object):
	def __init__(self, querytype, field, *values):
		self.querytype = querytype
		self.field = field
		self.values = values
		self.queries = None

	def add_children_query(self, *queries):
		self.queries = queries

	def get_children_querys(self):
		return self.queries

	def get_field(self):
		return self.field

	def get_values(self):
		return self.values

	def get_query_type(self):
		return self.querytype

# @app.route('/python/api/es/get_page', methods=['POST'])
# def get_page():
# 	# 使用Body中的x-www.form.urlencoded进行发送
# 	maps = request.values
# 	if len(maps) < 1:
# 		abort(400)
# 	index = maps["index"]
# 	queries = None
# 	page_index = 1
# 	page_size = 10
# 	order_fields = []
# 	order_dirs = []
# 	show_fields = []
# 	if "queries" in maps:
# 		queries = pickle.loads(maps["queries"])
# 	if "page_index" in maps:
# 		page_index = maps["page_index"]
# 	if "page_size" in maps:
# 		page_size = maps["page_size"]
# 	if "order_fields" in maps:
# 		order_fields = pickle.loads(maps["order_fields"])
# 	if "order_dirs" in maps:
# 		order_dirs = pickle.loads(maps["order_dirs"])
# 	if "show_fields" in maps:
# 		show_fields = pickle.loads(maps["show_fields"])
# 	result = get_page_core(index,queries,page_index,page_size,order_fields,order_dirs,show_fields)
# 	return jsonify(result), 200
#
# @app.route('/python/api/es/get_list', methods=['POST'])
# def get_list():
# 	# 使用Body中的x-www.form.urlencoded进行发送
# 	maps = request.values
# 	if len(maps) < 1:
# 		abort(400)
# 	index = maps["index"]
# 	queries = None
# 	size = 10
# 	order_fields = []
# 	order_dirs = []
# 	show_fields = []
# 	if "queries" in maps:
# 		queries = pickle.loads(maps["queries"])
# 	if "size" in maps:
# 		size = maps["size"]
# 	if "order_fields" in maps:
# 		order_fields = pickle.loads(maps["order_fields"])
# 	if "order_dirs" in maps:
# 		order_dirs = pickle.loads(maps["order_dirs"])
# 	if "show_fields" in maps:
# 		show_fields = pickle.loads(maps["show_fields"])
# 	result = get_list_core(index,queries,size,order_fields,order_dirs,show_fields)
# 	return jsonify(result), 200


host = "192.168.2.150"
alias_suffix = "alias"
esid_field = "esid"
delete_Field = "is_delete"
es_client = {}


def _get_client():
	if host not in es_client:
		# sniff_on_start:sniff before doing anything
		# sniff_on_connection_fail:refresh nodes after a node fails to respond
		# sniffer_timeout:and also every 60 seconds
		es = Elasticsearch(hosts=[{"host": host, "port": "9200"}], sniff_on_start=True, sniff_on_connection_fail=True,
						   sniffer_timeout=60)
		es_client[host] = es
	return es_client[host]


def _get_boolquery():
	return {"bool": {"should": [], "must": [], "must_not": []}}


def _wildcard_query(field, value):
	return {"wildcard": {field: "*{}*".format(value)}}


def _match_phrase_query(field, value):
	return {"match": {field: {"query": value, "type": "phrase"}}}


def _range_query(field, from_value=None, to_value=None, include_lower=True, include_upper=True):
	return {"range": {field: {"from": from_value, "to": to_value, "include_lower": include_lower, "include_upper": include_upper}}}


def _terms_query(field, *values):
	return {"terms": {field: values}}


def _match_query(field, value):
	return {"match": {field: {"query": value, "type": "boolean"}}}


def _ids_query(*values):
	return {"ids": {"values": [str(v) for v in values]}}


def _get_query_with_like(boolquery, field, value):
	if isinstance(value, int, float, bool):
		boolquery["bool"]["must"].append(_match_phrase_query(field, value))
	else:
		boolquery["bool"]["should"].append(_match_phrase_query("{}.raw".format(field), value))
		boolquery["bool"]["should"].append(_wildcard_query("{}.raw".format(field), value))
		boolquery["bool"]["should"].append(_match_phrase_query(field, value))
		boolquery["bool"]["should"].append(_wildcard_query(field, value))
	return boolquery


def _get_Core_Query(queryType, field, values):
	query = None
	filter = None
	if queryType:
		if QueryType.GT == queryType:
			filter = _range_query(field, from_value=values[0], include_lower=False)
		elif QueryType.LT == queryType:
			filter = _range_query(field, to_value=values[0], include_upper=False)
		elif QueryType.GE == queryType:
			filter = _range_query(field, from_value=values[0])
		elif QueryType.LE == queryType:
			filter = _range_query(field, to_value=values[0])
		elif QueryType.BN == queryType:
			filter = _range_query(field, from_value=values[0], to_value=values[1])
		elif QueryType.NI == queryType:  # NI是IN外面在套一个must_not
			len1 = len(values)
			if len1 == 1:
				query = _get_boolquery()
				query["bool"]["must_not"].append(_match_phrase_query(field, values[0]))
			else:
				boolquery = _get_boolquery()
				boolquery["bool"]["must_not"].append(_terms_query(field, *values))
				if len1 > 1000:
					filter = boolquery
				else:
					query = boolquery
		elif QueryType.IN == queryType:
			len1 = len(values)
			if len1 == 1:
				query = _match_phrase_query(field, values[0])
			else:
				if len1 > 1000:
					filter = _terms_query(field, *values)
				else:
					query = _terms_query(field, *values)
		elif QueryType.IN_LIKE == queryType:
			len1 = len(values)
			if len1 == 1:
				query = _get_query_with_like(_get_boolquery(), field, values[0])
			else:
				boolQuery = _get_boolquery()
				for value in values:
					boolQuery = _get_query_with_like(boolQuery, field, value)
				if len1 > 250:
					filter = boolQuery
				else:
					query = boolQuery
		elif QueryType.NL == queryType:
			query = _get_boolquery()
			query["bool"]["must_not"].append(_get_query_with_like(_get_boolquery(), field, values[0]))
		elif QueryType.LIKE == queryType:
			query = _get_query_with_like(_get_boolquery(), field, values[0])
		elif QueryType.LIKE_ANALYSE == queryType:
			query = _get_query_with_like(_get_boolquery(), field, values[0])
			query["bool"]["should"].append(_match_query(field, values[0]))
		elif QueryType.NE == queryType:
			filter = _get_boolquery()
			filter["bool"]["must_not"].append(_match_phrase_query(field, values[0]))
		elif QueryType.EQ == queryType:
			filter = _match_phrase_query(field, values[0])
	return (query, filter)


def _make_query_builder(q: Query, queryBuilder, filterBuilder, isAnd):
	if q.get_children_querys():
		chiqueryBuilder = None
		chifilterBuilder = None
		for chiQ in q.get_children_querys():
			boolQueryBuilders = _make_query_builder(chiQ, chiqueryBuilder, chifilterBuilder, False)
			chiqueryBuilder = boolQueryBuilders[0]
			chifilterBuilder = boolQueryBuilders[1]
		query = chiqueryBuilder
		filter = chifilterBuilder
	else:
		field = q.get_field()
		values = q.get_values()
		if values:
			if esid_field == field.lower():
				query = None
				filter = _ids_query(*values)
			else:
				queries = _get_Core_Query(q.get_query_type(), field, values)
				query = queries[0]
				filter = queries[1]
		else:
			raise Exception("查询字段:" + field + ",\t至少有1个值!")
	if query:
		if not queryBuilder:
			queryBuilder = _get_boolquery()
		if isAnd:
			queryBuilder["bool"]["must"].append(query)
		else:
			queryBuilder["bool"]["should"].append(query)
	if filter:
		if not filterBuilder:
			filterBuilder = _get_boolquery()
		if isAnd:
			filterBuilder["bool"]["must"].append(filter)
		else:
			filterBuilder["bool"]["should"].append(filter)
	return (queryBuilder, filterBuilder)


def _get_query_and_filter(queries):
	query = None
	filter = None
	if queries:
		for q in queries:
			builder = _make_query_builder(q, query, filter, True)
			query = builder[0]
			filter = builder[1]
	if not filter:
		filter = _get_boolquery()
	filter["bool"]["must_not"].append(_terms_query(delete_Field, True))
	return (query, filter)


# 根据分页参数获取起始位置
def _get_from_index(pageindex, pagesize):
	if pageindex < 1:
		pageindex = 1
	return (pageindex - 1) * pagesize


# 获取排序对象
def _get_sort(field, value):
	if value:
		return {field: {"order": "asc"}}
	return {field: {"order": "desc"}}


# 获取es查询dsl(由query,filter,排序方式组成)
def _get_body(query=None, filter=None, order_fields=[], order_dirs=[]):
	if query and filter:
		body = {"query": query, "post_filter": filter}
	elif query:
		body = {"query": query}
	elif filter:
		body = {"post_filter": filter}
	else:
		body = None
	# 有排序字段
	if order_fields:
		len1 = len(order_fields)
		if not order_dirs:
			order_dirs = []
		len2 = len(order_dirs)
		# 排序方式数量小于排序字段,则使用升序方式
		if len1 > len2:
			for i in range(len2, len1):
				order_dirs.append(1)
		# 组装成es排序对象
		ls = []
		for i in range(len1):
			ls.append(_get_sort(order_fields[i], order_dirs[i]))
		if not body:
			body = {}
		body["sort"] = ls
	return body


def _get_result_from_search(search):
	result = []
	for d in search['hits']['hits']:
		model = d["_source"]
		model["esid"] = d["_id"]
		result.append(model)
	return result


def get_page_core(index, queries=None, page_index=1, page_size=10, order_fields=[], order_dirs=[], show_fields=[]):
	es = _get_client()
	index = index.lower() + alias_suffix
	query = _get_query_and_filter(queries)
	body = _get_body(query[0], query[1], order_fields, order_dirs)
	search = es.search(index=index, body=body, from_=_get_from_index(page_index, page_size), size=page_size,
					   _source_include=show_fields)
	return {"items": _get_result_from_search(search), "total": search["hits"]["total"]}


def get_list_core(index, queries=None, size=10, order_fields=[], order_dirs=[], showfields=[]):
	"""

	:param index:
	:param queries:
	:param size:要获取的条数,-1则获取全部数据
	:param order_fields:
	:param order_dirs:
	:param showfields:
	:return:
	"""
	es = _get_client()
	index = index.lower() + alias_suffix
	query = _get_query_and_filter(queries)
	body = _get_body(query[0], query[1], order_fields, order_dirs)
	default_size = 1000
	# default_size = 10
	if size < default_size and size != -1:
		default_size = size
	# 先获取一次, 再循环获取
	result = []
	search = es.search(index=index, body=body, size=default_size, _source_include=showfields, scroll="1m")
	deal_result = _get_result_from_search(search)
	if deal_result:
		result += deal_result
		scroll_id = search["_scroll_id"]
		while len(result) < size or size == -1:
			scroll = es.scroll(scroll_id, scroll="1m")
			deal_result = _get_result_from_search(scroll)
			if deal_result:
				result += deal_result
			else:
				break
	return {"items": result}


if __name__ == '__main__':
	result=get_page_core("accesslogs", [Query(QueryType.BN, "time_local", "2017-09-05T16:52:19.000Z","2018-09-05T16:52:19.000Z")])
	print(result)
	# l = get_list_core("audit", size=-1, order_fields=["edit_user_id", "audit_date"], order_dirs=[1, 0],
	# 				  showfields=["edit_user_id", "audit_date"])
	# print(l)
	# print(len(l))



	# aa = [Query(QueryType.IN, "esid", 1, 2, 3)]
	# encodedjson = json.dumps(aa)
	# print(encodedjson)
	# bb=json.loads(encodedjson)
	# print(bb)
	#
	# print(1)
