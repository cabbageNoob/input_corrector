# coding: utf-8

from __future__ import (print_function, unicode_literals)

import os
import sys

sys.path = ['../..'] + sys.path
from Pinyin2Hanzi import util

try:
    reload(sys)
    sys.setdefaultencoding('utf-8')
except:
    pass

SOURCE_FILE           = './hanzipinyin.txt'

ALL_STATES_FILE       = './result/all_states.txt'         # 汉字（隐藏状态）
ALL_OBSERVATIONS_FILE = './result/all_observations.txt'   # 拼音（观测值）
PINYIN2HANZI_FILE     = './result/pinyin2hanzi.txt'
ALL_PINYIN_FILE       = './result/all_pinyin.txt'

states = set()
observations = set()
py2hz = {}
all_pinyin=set()


for line in open(SOURCE_FILE,'rb'):
    line = util.as_text(line.strip())
    hanzi, pinyin_list = line.split('=')
    pinyin_list = [util.simplify_pinyin(item.strip()) for item in pinyin_list.split(',')]

    states.add(hanzi)
    
    for pinyin in pinyin_list:
        observations.add(pinyin)
        py2hz.setdefault(pinyin, set())
        py2hz[pinyin].add(hanzi)
        # 声母
        shengmu = util.get_shengmu(pinyin)
        if shengmu is not None:
            py2hz.setdefault(shengmu, set())
            py2hz[shengmu].add(hanzi)

 # 声母
__shengmu = set(['b', 'p', 'm', 'f', 'd', 't', 'n', 'l', 'g', 'k', 'h', 'j', 'q', 'x', 'zh',\
            'ch', 'sh', 'r', 'z', 'c', 's', 'y', 'w'])
all_pinyin = __shengmu|observations

with open(ALL_STATES_FILE, 'w',encoding='utf8') as out:
    s = '\n'.join(states)
    out.write(s)

with open(ALL_OBSERVATIONS_FILE, 'w',encoding='utf8') as out:
    s = '\n'.join(observations)
    out.write(s)

with open(PINYIN2HANZI_FILE, 'w',encoding='utf8') as out:
    s = ''
    for k in py2hz:
        s = s + k + '=' + ''.join(py2hz[k]) + '\n'
    out.write(s)

with open(ALL_PINYIN_FILE, 'w', encoding='utf8') as out:
    s='\n'.join(all_pinyin)
    out.write(s)

print('end')