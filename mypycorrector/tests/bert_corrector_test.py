'''
@Descripttion: 
@version: 
@Author: cjh <492795090@qq.com>
@Date: 2020-02-24 10:30:07
@LastEditors: cjh <492795090@qq.com>
@LastEditTime: 2020-03-30 11:10:40
'''
# -*- coding: utf-8 -*-
"""
@author:cjh（492795090@qq.com)
@data:19-11-25
@description: 
"""
import sys
import os
sys.path.append("../")
sys.path.append(os.getcwd())
# from mypycorrector.bert import bert_corrector
from mypycorrector.bert_new import bert_corrector

error_sentences = [
    '汽车新式在这条路上',
    '中国人工只能布局很不错',
    '想不想在来一次比赛',
    '你不觉的高兴吗',
    '权利的游戏第八季',
    '美食美事皆不可辜负，这场盛会你一定期待已久',
    '点击咨询痣疮是什么原因?咨询医师痣疮原因',
    '附睾焱的症状?要引起注意!',
    '外阴尖锐涅疣怎样治疗?-济群解析',
    '洛阳大华雅思 30天突破雅思7分',
    '男人不育少靖子症如何治疗?专业男科,烟台京城医院',
    '疝気医院那好 疝気专科百科问答',
    '成都医院治扁平苔鲜贵吗_国家2甲医院',
    '少先队员因该为老人让坐',
    '服装店里的衣服各试各样',
    '一只小鱼船浮在平净的河面上',
    '我的家乡是有明的渔米之乡',
    ' _ ,',
    '我对于宠物出租得事非常认同，因为其实很多人喜欢宠物',  # 出租的事
    '有了宠物出租地方另一方面还可以题高人类对动物的了解，因为那些专业人氏可以指导我们对于动物的习惯。',  # 题高 => 提高 专业人氏 => 专业人士
    '三个凑皮匠胜过一个诸葛亮也有道理。',  # 凑
    '还有广告业是只要桌子前面坐者工作未必产生出来好的成果。',
]

badcase = ['这个跟 原木纯品 那个啥区别？不是原木纸浆做的?',
           '能充几次呢？',
           '这是酸奶还是像饮料一样的奶？',
           '现在银色的K2P是MTK还是博通啊？',
           '是浓稠的还是稀薄的？',
           '这个到底有多辣',
           'U盘有送挂绳吗 ',
           '果子酸吗？有烂的吗？',
           '刚下单买了一箱，需要明天到货，先问下味道如何',
           '2周岁22斤宝宝用多大的啊？',
           '请问这茶是一条装的吗',
           '有坏的果吗',
           '生产日期怎么样 新嘛',
           '插上去的时候是驱蚊液放下面的吗？',
           '橄榄的和这款哪个比较好用？味道都是一样的么？',
           ]
error_sentences.extend(badcase)

bertCorrector = bert_corrector.BertCorrector()
bertCorrector.enable_word_error(enable=False)
for line in error_sentences:
    correct_sent = bertCorrector.bert_correct(line)
    print("original sentence:{} => correct sentence:{}".format(line, correct_sent))
