#! /usr/bin/python3.5
# -*- coding:utf-8 -*-
import nltk
from nltk.corpus import PlaintextCorpusReader

corpus_root = '../sources/'

allText = ''

allText = PlaintextCorpusReader(corpus_root, ['comment4.txt', 'comment5.txt'])

print(type(allText))

sinica_text = nltk.Text(allText.words())
the_set = set(sinica_text)

mytexts = nltk.TextCollection(allText)

print(len(mytexts._texts))

print(len(mytexts))


print(len(the_set))
for tmp in the_set:
	print(tmp, "tf", mytexts.tf(tmp, allText.raw(['comment4.txt'])), "idf", mytexts.idf(tmp), mytexts.tf_idf(tmp, allText.raw(['comment4.txt'])))
