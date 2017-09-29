#!/usr/bin/python3.5
# -*- coding:utf-8 -*-

import os, sys, re, time

sys.path.append('/home/esuser/NLP35')
import jieba

from utils import IOUtils

path = IOUtils.get_path_target("match_jieba_drug_exact_discover.txt")
tokenizer = jieba.Tokenizer(path)

text = "清热祛湿-耐克替尼"
resultset = tokenizer.cutwkz_set(text)
print(resultset)
