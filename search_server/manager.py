# -*- coding: UTF-8 -*-
from flask import Flask,render_template,redirect,request
import pymysql
import jieba
import time
import pandas as pd
import json
import pypinyin

import sys
sys.path.insert(0,r'D:\LMModel\pycorrector')
from pycorrector10 import correct
app=Flask(__name__)
print(correct("佳如爱有天意"))

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
    pred_sentences, pred_detail = correct(sentence)
    # pred_sentences.append({'pred_sentence':pred_sentence})
    for sentence,ppl in pred_sentences.items():
        sentences_maybe.append({'ppl_score':ppl,'sentence':sentence})
    response['pred_sentences']=sentences_maybe
    return json.dumps(response)

if __name__=='__main__':
    app.run(host='127.0.0.1',port=8001)