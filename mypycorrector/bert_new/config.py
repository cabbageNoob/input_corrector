'''
@Descripttion: 
@version: 
@Author: cjh (492795090@qq.com)
@Date: 2020-03-18 07:33:36
@LastEditors: cjh <492795090@qq.com>
@LastEditTime: 2020-03-20 16:34:40
'''
# -*- coding: utf-8 -*-

import os

pwd_path = os.path.abspath(os.path.dirname(__file__))

bert_model_dir = os.path.join(pwd_path, '../data/bert_models/chinese_finetuned_lm/')
# bert_model_dir = r'D:\LMModel\origin\pycorrector\pycorrector\data\bert_models\chinese_finetuned_lm'
bert_model_path = os.path.join(pwd_path, '../data/bert_models/chinese_finetuned_lm/pytorch_model.bin')
# bert_model_path = r'D:\LMModel\origin\pycorrector\pycorrector\data\bert_models\chinese_finetuned_lm\pytorch_model.bin'
bert_config_path = os.path.join(pwd_path, '../data/bert_models/chinese_finetuned_lm/config.json')
# bert_model_vocab = os.path.join(pwd_path, '../data/bert_models/chinese_finetuned_lm/vocab.txt')
