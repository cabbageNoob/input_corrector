'''
@Descripttion: 
@version: 
@Author: cjh (492795090@qq.com)
@Date: 2020-03-18 07:33:36
@LastEditors: cjh <492795090@qq.com>
@LastEditTime: 2020-05-01 11:07:11
'''
# -*- coding: utf-8 -*-

import os

pwd_path = os.path.abspath(os.path.dirname(__file__))

bert_model_dir = os.path.join(pwd_path, '../data/bert_models/chinese_finetuned_lm/')
bert_model_path = os.path.join(pwd_path, '../data/bert_models/chinese_finetuned_lm/pytorch_model.bin')
bert_config_path = os.path.join(pwd_path, '../data/bert_models/chinese_finetuned_lm/config.json')

# ssc音形码文件
hanzi_ssc_path = os.path.join(pwd_path, '../data/ssc_data/hanzi_ssc_res.txt')
# 生成score_data 文件
score_2013_data_path = os.path.join(pwd_path, '../data/cn/sighan/score_data/score_data_sighan_2013.txt')
score_2013_data_new_path = os.path.join(pwd_path, '../data/cn/sighan/score_data/score_data_segment_punc_test.txt')
score_2015_A2_data_path = os.path.join(pwd_path, '../data/cn/sighan/score_data/score_data_sighan_2015_A2.txt')

score_2013_dry_path = os.path.join(pwd_path, '../data/cn/sighan/score_data/score_data_sighan_2013_dry.txt')
score_2014_dry_path = os.path.join(pwd_path, '../data/cn/sighan/score_data/score_data_sighan_2014_dry.txt')
score_2015_dry_path = os.path.join(pwd_path, '../data/cn/sighan/score_data/score_data_sighan_2015_dry.txt')

# neural_network model path
# neural_network_model_path = os.path.join(pwd_path, '../data/network_new.pth')
neural_network_model_path = os.path.join(pwd_path, '../data/network_segment_punc.pth')
