'''
@Descripttion: config file
@version: 
@Author: cjh <492795090@qq.com>
@Date: 2019-12-19 11:20:11
@LastEditors  : cjh <492795090@qq.com>
@LastEditTime : 2019-12-22 10:01:38

'''
# -*- coding: utf-8 -*-
# Author: cjh<492795090@qq.com>
# Date: 19-12-01
# Brief: config

import os

pwd_path = os.path.abspath(os.path.dirname(__file__))
# 通用分词词典文件  format: 词语 词频
word_freq_path = os.path.join(pwd_path, 'data/word_freq.txt')
# 中文常用字符集
common_char_path = os.path.join(pwd_path, 'data/common_char_set.txt')
# 同音字
same_pinyin_path = os.path.join(pwd_path, 'data/same_pinyin.txt')
# 形似字
same_stroke_path = os.path.join(pwd_path, 'data/same_stroke.txt')
# language model path
language_model_path = os.path.join(pwd_path, 'data/kenlm/zh_giga.no_cna_cmn.prune01244.klm')#people2014corpus_chars.klm  #THUCNews_char.klm  #THUCNews_people2014_merge_char.klm
kenlm_ngram_query_path = os.path.join(pwd_path, 'kenlm_ngram_query_x64.exe')

# 用户自定义错别字混淆集  format:变体	本体   本体词词频（可省略）
custom_confusion_path = os.path.join(pwd_path, 'data/custom_confusion.txt')
# 用户自定义分词词典  format: 词语 词频
custom_word_freq_path = os.path.join(pwd_path, 'data/custom_word_freq.txt')
# 知名人名词典 format: 词语 词频
person_name_path = os.path.join(pwd_path, 'data/person_name.txt')
# 地名词典 format: 词语 词频
place_name_path = os.path.join(pwd_path, 'data/place_name.txt')
# 停用词
stopwords_path = os.path.join(pwd_path, 'data/stopwords.txt')
# RNN语言模型
rnnlm_vocab_path = os.path.join(pwd_path, 'rnn_lm/output/word_freq.txt')
rnnlm_model_dir = os.path.join(pwd_path, 'rnn_lm/output/model/')
