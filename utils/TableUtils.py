#!/usr/bin/python3.5
# -*- coding:utf-8 -*-

import os, sys, re, time
import xlrd
import xlwt


def _read_xlsx_data(booksheet, rowindexes, colindexes):
	rows = []
	for rowindex in rowindexes:
		row_data = []
		for colindex in colindexes:
			cel = booksheet.cell(rowindex, colindex)
			val = cel.value
			if type(val) == str:
				val = val.lstrip()
			else:
				val = str(val).lstrip()
			row_data.append(val)
		rows.append(row_data)
	return rows


def read_xlsx(file, colindexes="*", istitle=False):
	"""
	读取xlsx文件
	:param file:文件路径
	:param colindex:colindexes默认读取全部列,设置集合[0,3]可以读取指定列
	:param sheet:sheet名称
	:param istitle:是否包含标题
	:return:返回list
	"""
	workbook = xlrd.open_workbook(file)
	# booksheet = workbook.sheet_by_name(sheet)
	booksheet = workbook.sheet_by_index(0)
	# 判断是否含有标题,有标题则过滤掉第一行
	if istitle:
		rowindexes = range(1, booksheet.nrows)
	else:
		rowindexes = range(booksheet.nrows)
	# 获取所有列
	if colindexes == "*":
		return _read_xlsx_data(booksheet, rowindexes, range(booksheet.ncols))
	else:
		return _read_xlsx_data(booksheet, rowindexes, colindexes)


def write_xlsx(file, data):
	"""
	write_xlsx(os.path.join("..","wkztarget","wkzhaha"),[("t1","t2","t3"),[1,2,3],[4,5,6]])
	:param file: 文件路径
	:param data: 集合嵌套集合的数据,类似:[("t1","t2","t3"),[1,2,3],[4,5,6]]
	:return:None
	"""
	wbk = xlwt.Workbook(encoding='utf-8', style_compression=0)
	# 第二参数用于确认同一个cell单元是否可以重设值。
	sheet = wbk.add_sheet("Sheet1", cell_overwrite_ok=True)
	for i in range(len(data)):
		row = data[i]
		for j in range(len(data[i])):
			sheet.write(i, j, row[j])
	# 设置样式
	# style = xlwt.XFStyle()
	# font = xlwt.Font()
	# # font.name = 'Times New Roman'
	# font.bold = False
	# style.font = font
	# sheet.write(0, 1, 'some bold Times text', style)

	if not file.endswith(".xlsx"):
		file += ".xlsx"
	wbk.save(file)
