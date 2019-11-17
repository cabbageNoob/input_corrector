# -*- coding: UTF-8 -*-
from flask import Flask,render_template,redirect,request
import pymysql
import jieba
import time
import pandas as pd
import json
import pypinyin
import sys
import os

from pycorrector import correct
from pinyin2chinese import cut
from pinyin2chinese.pinyincut import Trie
from pinyin2chinese.pinyincut import TrieNode

from Pinyin2Hanzi import DefaultHmmParams
from Pinyin2Hanzi import viterbi

app=Flask(__name__)
# print(correct("佳如爱有天意"))
# print(cut('zhegexiaogegezhenshuai'))

@app.route("/",methods=["GET", "POST"])
def index():
    correct('你好')#初始化
    return render_template("search.html")

@app.route("/get_maybe_sentence",methods=["DET","POST"])
def get_maybe_sentence():
    response = dict()
    sentences_maybe=list()
    sentence=request.form['sentence']
    print(sentence)
    if is_pinyin(sentence):
        pinyin_list = cut(sentence)
        pred_sentences = pinyin2hanzi(pinyin_list)
    else:
        pred_sentences, pred_detail = correct(sentence)
    for sentence,ppl in pred_sentences.items():
        sentences_maybe.append({'ppl_score':ppl,'sentence':sentence})
    response['pred_sentences']=sentences_maybe
    return json.dumps(response)

#判断sentence是否为拼音
def is_pinyin(sentence):
    return sentence.encode('utf8').isalpha()
#将拼音列表转换为汉字
def pinyin2hanzi(pinyin_list):
    pred_sentences=dict()
    hmmparams = DefaultHmmParams()
    ## 1个候选
    result = viterbi(hmm_params=hmmparams, observations=tuple(pinyin_list), path_num=5,log = True)
    for item in result:
        pred_sentences[''.join(item.path)]=item.score
    return pred_sentences
if __name__=='__main__':
    # print(is_pinyin("xiaogegezhenshuai"))
    # print(is_pinyin("小哥哥真帅"))
    app.run(host='127.0.0.1',port=8001)