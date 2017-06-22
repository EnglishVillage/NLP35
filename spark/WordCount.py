#!/usr/bin/python3.5
# -*- coding:utf-8 -*-

from pyspark import SparkContext, SparkConf

if __name__ == '__main__':
	conf = SparkConf().setAppName("aa").setMaster("local[3]")
	sc = SparkContext(conf=conf)
	lines = sc.textFile('d:/tmp/lastzero.txt')
	counts = lines.flatMap(lambda x: x.split('\t')).map(lambda x: (x, 1)).reduceByKey(lambda x, y: x + y).sortBy(lambda x:x[1],False)
	output = counts.collect()
	for (word, count) in output:
		print("%s: %i" % (word, count))
	sc.stop()
