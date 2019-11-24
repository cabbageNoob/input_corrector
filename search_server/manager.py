# -*- coding: UTF-8 -*-
from flask import Flask,render_template,redirect,request
import json
import re
import util
import sys
import os

from pycorrector import correct
from Pinyin2Hanzi import cut
from Pinyin2Hanzi.pinyincut import Trie
from Pinyin2Hanzi.pinyincut import TrieNode

from Pinyin2Hanzi import DefaultHmmParams
from Pinyin2Hanzi import viterbi

app=Flask(__name__)
DEFAULTSCORE=-10.

POSTING_FILE='../train/hmm/result/postinglist_final.json'
posting_data=util.readjson(POSTING_FILE)
print(len(posting_data))

correct('你好')
cut('')

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
    sentence=request.form['sentence']
    print(sentence)
    if is_pinyin(sentence):
        #得到的全是拼音
        pinyin_list = cut(sentence)
        print(pinyin_list)
        pred_sentences = pinyin2hanzi(pinyin_list)
    else:
        #提取出拼音部分，并转换为汉字
        sentence=pre_process(sentence)
        pred_sentences, pred_detail = correct(sentence)
    #将拼音转化为汉字后，无错误情况
    if not pred_sentences:
        sentences_maybe.append({'score': DEFAULTSCORE, 'sentence': sentence})
    for sentence,score in pred_sentences.items():
        sentences_maybe.append({'score':score,'sentence':sentence})
    response['pred_sentences']=sentences_maybe
    return json.dumps(response)

#判断sentence是否为拼音
def is_pinyin(sentence):
    return sentence.encode('utf8').isalpha()
#将拼音列表转换为汉字
def pinyin2hanzi(pinyin_list):
    pred_sentences=dict()
    if len(pinyin_list)<=2:
        path_score = sorted(posting_data[''.join(pinyin_list)].items(),\
                            key=lambda x: x[1], reverse=True)
        return dict(path_score)
    else:
        i=0
        score=0
        path=''
        while(2*i<len(pinyin_list)):
            pinyin_cur=''.join(pinyin_list[2*i:2*(i+1)])
            i+=1
            path_score=sorted(posting_data[pinyin_cur].items(),key=lambda x:x[1],reverse=True)
            path+=path_score[0][0]
            score+=path_score[0][1]
        pred_sentences[path]=score
        return pred_sentences

    # pred_sentences=dict()
    # hmmparams = DefaultHmmParams()
    # ## 1个候选
    # result = viterbi(hmm_params=hmmparams, observations=tuple(pinyin_list), \
    #                  path_num=5,log = True)
    # for item in result:
    #     pred_sentences[''.join(item.path)]=item.score
    # return pred_sentences

def pre_process(sentence):
    result=re.sub('[a-z]+',repl,sentence)
    return result

def repl(matched):
    value=str(matched.group())
    pinyin_list=cut(value)
    return list(pinyin2hanzi(pinyin_list).keys())[0]
    # hmmparams = DefaultHmmParams()
    # return ''.join(viterbi(hmm_params=hmmparams, observations=tuple(cut(value)),\
    #                        path_num=1,log = True)[0].path)

if __name__=='__main__':
    app.run(host='127.0.0.1',port=8001)
    # pinyin2hanzi(['d','n','w'])