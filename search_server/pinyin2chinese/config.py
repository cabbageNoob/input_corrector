# -*- coding: utf-8 -*-
# Author: cjh <492795090@qq.com>
# Brief: config

import os
pwd_path = os.path.abspath(os.path.dirname(__file__))
#字典树模型文件
trie_path = os.path.join(pwd_path, 'data/pinyin_trie.model')
#拼音文件
pinyin_path=os.path.join(pwd_path, 'data/pinyin.txt')