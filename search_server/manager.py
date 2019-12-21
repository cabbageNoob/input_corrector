'''
@Descripttion: 
@version: 
@Author: Jiahao
@Date: 2019-12-12 10:59:28
@LastEditors  : cjh <492795090@qq.com>
@LastEditTime : 2019-12-21 21:30:41
'''
# -*- coding: UTF-8 -*-
import json
import re
import sys
import os
sys.path.insert(0, os.getcwd())
from mypycorrector import correct
from Pinyin2Hanzi import cut
from Pinyin2Hanzi.pinyincut import Trie
from Pinyin2Hanzi.pinyincut import TrieNode
from Pinyin2Hanzi import DefaultHmmParams
from Pinyin2Hanzi import viterbi
import util
from flask import Flask, render_template, redirect, request


app = Flask(__name__)
DEFAULTSCORE = -10.


correct('你好')
cut('')
value_candidate = {}


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("search.html")


@app.route("/get_maybe_sentence", methods=["GET", "POST"])
def get_maybe_sentence():
    response = dict()
    sentences_maybe = list()
    details_ = list()
    sentence = request.form['sentence']
    is_allpinyin = False
    is_allhanzi = False
    hanzi_pinyin = False
    sentence.replace(' ',"\'")
    print(sentence)
    if util.is_pinyin(sentence):
        # 得到的全是拼音
        pinyin_list = cut(sentence)
        pred_sentences = util.pinyin2hanzi(pinyin_list)
        detail_word = [sentence, list(pred_sentences.keys())[0], 0, len(sentence)]
        details_.append(detail_word)
        is_allpinyin=True
    elif util.contain_pinyin(sentence):
        # 提取出拼音部分，并转换为汉字
        candidates,details = pre_process(sentence)
        scores = util.sentence_score(candidates)
        pred_sentences = {candidate: score for candidate, score in zip(candidates, scores)}
        hanzi_pinyin=True
    else:
        # 全是汉字
        pred_sentences, pred_detail = correct(sentence)
        details = pred_detail
        is_allhanzi=True
    # 将拼音转化为汉字后，无错误情况
    print('pred_sentences', pred_sentences)
    for sentence, score in pred_sentences.items():
        if is_allhanzi:
            details_=[[detail[0],sentence[detail[1]:detail[2]],detail[1],detail[2]] for detail in details]
            sentences_maybe.append({'score': score, 'sentence': sentence, 'detail': details_})
        if is_allpinyin:
            sentences_maybe.append({'score': score, 'sentence': sentence, 'detail': details_})
        if hanzi_pinyin:
            details_=[[detail[0],sentence[detail[1]:detail[2]],detail[1],detail[2]] for detail in details]
            sentences_maybe.append({'score': score, 'sentence': sentence, 'detail': details_})
    response['pred_sentences'] = sentences_maybe
    return json.dumps(response, ensure_ascii=False)


def pre_process(sentence):
    global value_candidate
    value_candidate = {}
    result = re.sub('[a-z]+', repl, sentence)
    return util.get_candidates([result], value_candidate)


def repl(matched):
    global value_candidate
    value = str(matched.group())
    pinyin_list = cut(value)
    candidate = list(util.pinyin2hanzi(pinyin_list).keys())
    value_candidate.setdefault(value, [])
    value_candidate[value] = candidate
    print('value_candidate', value_candidate)
    return '*'*len(pinyin_list)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001)
    
