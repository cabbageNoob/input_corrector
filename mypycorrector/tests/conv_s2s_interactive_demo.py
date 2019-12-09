# -*- coding: utf-8 -*-
"""
@author:cjh（492795090@qq.com)
@data:19-11-25
@description: 
"""

import sys

sys.path.append("../")
from pycorrector.conv_seq2seq.infer import infer_interactive
from pycorrector.conv_seq2seq import config

print(">")
# 通过交互输入预测
outputs = infer_interactive(model_path=config.best_model_path,
                            vocab_dir=config.data_bin_dir,
                            arch=config.arch,
                            max_len=config.max_len)
print("output:", outputs)
# input: 少 先 队 员 因 该 为 老 人 让 坐
