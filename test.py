'''
@Descripttion: 
@version: 
@Author: cjh <492795090@qq.com>
@Date: 2019-12-16 14:22:45
@LastEditors  : cjh <492795090@qq.com>
@LastEditTime : 2019-12-21 23:26:48
'''
import kenlm
import sys, os
sys.path.insert(0,os.getcwd())
from mypycorrector.lm_query import KenLMQuery
lm = kenlm.Model(r'C:\Users\cjh\.pycorrector\datasets\zh_giga.no_cna_cmn.prune01244.klm')
# text = '第 5 代 移动 通信 技术 （ 以下 简称 “ 5G ” ）致力 于 解决 爆炸 性 移动 数据流 的 增长 ， 海量 设备 的 连接 以及 不断 涌现 的 新 业务 和 新 应用'
# print('score',lm.score(text))
# print('perplexity',lm.perplexity(text))

# with open('score.txt', 'r', encoding = 'utf8') as f:
#     data = f.readlines()[0]
# data = data.split('=')
# sum=0.
# for d in data[1:]:
#     sum+=float(d.split()[2])

# print(data)
# print(sum)
# scores=lm.score('北 京 理 工 大 学')
# print(scores)

kenlmquery = KenLMQuery(model=r'C:\Users\cjh\.pycorrector\datasets\zh_giga.no_cna_cmn.prune01244.klm', \
         execute=r'D:\LMModel\pycorrector_git\mypycorrector\kenlm_ngram_query_x64.exe')
print(kenlmquery.perplexity('北 京 理 工 大 学'))
print(lm.perplexity('北 京 理 工 大 学'))