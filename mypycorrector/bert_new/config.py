'''
@Descripttion: 
@version: 
@Author: cjh (492795090@qq.com)
@Date: 2020-03-18 07:33:36
@LastEditors: cjh <492795090@qq.com>
@LastEditTime: 2020-03-29 13:31:49
'''
# -*- coding: utf-8 -*-

import os

pwd_path = os.path.abspath(os.path.dirname(__file__))

bert_model_dir = os.path.join(pwd_path, '../data/bert_models/chinese_finetuned_lm/')
# bert_model_dir = r'D:/LMModel/pycorrector_git/mypycorrector/data/bert_models/chinese_finetuned_lm/'
bert_model_path = os.path.join(pwd_path, '../data/bert_models/chinese_finetuned_lm/pytorch_model.bin')
# bert_model_path = r'D:/LMModel/pycorrector_git/mypycorrector/data/bert_models/chinese_finetuned_lm/pytorch_model.bin'
bert_config_path = os.path.join(pwd_path, '../data/bert_models/chinese_finetuned_lm/config.json')
# bert_config_path = r'D:/LMModel/pycorrector_git/mypycorrector/data/bert_models/chinese_finetuned_lm/config.json'

# ssc音形码文件
hanzi_ssc_path = os.path.join(pwd_path, '../data/ssc_data/hanzi_ssc_res.txt')