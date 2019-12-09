# -*- coding: utf-8 -*-
"""
@author:cjh（492795090@qq.com)
@data:19-11-25
@description: 
"""

import os

pwd_path = os.path.abspath(os.path.dirname(__file__))

bert_model_dir = os.path.join(pwd_path, '../data/bert_models/chinese_finetuned_lm')
bert_model_vocab = os.path.join(pwd_path, '../data/bert_models/chinese_finetuned_lm/vocab.txt')
output_dir = os.path.join(pwd_path, './output')
max_seq_length = 128
threshold = 0.1
