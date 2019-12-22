'''
@Descripttion: 
@version: 
@Author: cjh <492795090@qq.com>
@Date: 2019-12-20 13:50:14
@LastEditors  : cjh <492795090@qq.com>
@LastEditTime : 2019-12-20 15:07:26
'''
import sys, os
sys.path.insert(0, os.getcwd())

from mypycorrector import correct
print(correct('涧了我一身水'))
# import kenlm
# model = kenlm.LanguageModel('./data/kenlm/people2014corpus_chars.klm')
# score=model.score("我额单鹄寡凫波斯尼亚们要去 天 安 门")
# print(score)