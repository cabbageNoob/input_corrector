# -*- coding: UTF-8 -*-
from flask import Flask,render_template,redirect,request
import json
import re
import util

from pycorrector import correct

from Pinyin2Hanzi import cut
from Pinyin2Hanzi.pinyincut import Trie
from Pinyin2Hanzi.pinyincut import TrieNode

from Pinyin2Hanzi import DefaultHmmParams
from Pinyin2Hanzi import viterbi

app=Flask(__name__)
DEFAULTSCORE=-10.

# print(len(posting_data))

correct('你好')
cut('')
value_candidate={}

def readjson(filename):
    with open(filename, 'rb') as outfile:
        return json.load(outfile)

@app.route("/",methods=["GET", "POST"])
def index():
    return render_template("search.html")

@app.route("/get_maybe_sentence",methods=["DET","POST"])
def get_maybe_sentence():
    response = dict()
    sentences_maybe=list()
    value_candidate={}
    sentence=request.form['sentence']
    print(sentence)
    if util.is_pinyin(sentence):
        #得到的全是拼音
        pinyin_list = cut(sentence)
        pred_sentences = util.pinyin2hanzi(pinyin_list)
    elif util.contain_pinyin(sentence):
        #提取出拼音部分，并转换为汉字
        candidates=pre_process(sentence)
        scores=util.sentence_score(candidates)
        pred_sentences={candidate:score for candidate,score in zip(candidates,scores)}
    else:
        #全是汉字
        pred_sentences, pred_detail = correct(sentence)
    #将拼音转化为汉字后，无错误情况
    if not pred_sentences:
        sentences_maybe.append({'score': DEFAULTSCORE, 'sentence': sentence})
    for sentence,score in pred_sentences.items():
        sentences_maybe.append({'score':score,'sentence':sentence})
    response['pred_sentences']=sentences_maybe
    return json.dumps(response)


def pre_process(sentence):
    global value_candidate
    value_candidate={}
    result=re.sub('[a-z]+',repl,sentence)
    return util.get_candidates([result],value_candidate)

def repl(matched):
    global value_candidate
    value=str(matched.group())
    print('value',value)
    pinyin_list=cut(value)
    candidate=list(util.pinyin2hanzi(pinyin_list).keys())
    value_candidate.setdefault(value,[])
    value_candidate[value]=candidate
    print('value_candidate',value_candidate)
    return '*'*len(value)



def test():
    s='zhegexiaogege'
    print(util.pinyin2hanzi(cut(s)))

if __name__=='__main__':
    app.run(host='127.0.0.1',port=8001)
    # test()
    # get_candidates(['***如**有天意'],index_candidate)
    # print(index_candidate)

