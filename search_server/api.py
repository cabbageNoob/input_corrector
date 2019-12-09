# -*- coding: UTF-8 -*-
# Author: cjh<492795090@qq.com>
# Date: 19-12-01
import json
import re
import sys
import os
sys.path.insert(0, os.getcwd())
from Pinyin2Hanzi import viterbi
from Pinyin2Hanzi import DefaultHmmParams
from Pinyin2Hanzi.pinyincut import Trie, TrieNode
from Pinyin2Hanzi import cut
from mypycorrector import correct
import util
from flask import Flask, request
from flask_restful import Resource, Api


app = Flask(__name__)
api = Api(app)
DEFAULTSCORE = -10.

correct('你好')
cut('')
value_candidate = {}


class GetSentences(Resource):
    def post(self):
        response = dict()
        sentences_maybe = list()
        sentence = request.form['sentence']
        print(sentence)
        if util.is_pinyin(sentence):
            # 得到的全是拼音
            pinyin_list = cut(sentence)
            pred_sentences = util.pinyin2hanzi(pinyin_list)
        elif util.contain_pinyin(sentence):
            # 提取出拼音部分，并转换为汉字
            candidates = pre_process(sentence)
            scores = util.sentence_score(candidates)
            pred_sentences = {candidate: score for candidate,
                              score in zip(candidates, scores)}
        else:
            # 全是汉字
            pred_sentences, pred_detail = correct(sentence)
        # 将拼音转化为汉字后，无错误情况
        for sentence, score in pred_sentences.items():
            sentences_maybe.append({'score': score, 'sentence': sentence})
        response['pred_sentences'] = sentences_maybe
        print(response)
        return json.dumps(response, ensure_ascii=False)


def pre_process(sentence):
    global value_candidate
    value_candidate = {}
    result = re.sub('[a-z]+', repl, sentence)
    return util.get_candidates([result], value_candidate)

def repl(matched):
    global value_candidate
    value = str(matched.group())
    print('value', value)
    pinyin_list = cut(value)
    candidate = list(util.pinyin2hanzi(pinyin_list).keys())
    value_candidate.setdefault(value, [])
    value_candidate[value] = candidate
    print('value_candidate', value_candidate)
    return '*'*len(value)


api.add_resource(GetSentences,
                 '/',
                 '/get_maybe_sentence')
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8002)
