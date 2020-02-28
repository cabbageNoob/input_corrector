'''
@Descripttion: 
@version: 
@Author: cjh <492795090@qq.com>
@Date: 2020-02-24 15:22:22
@LastEditors: cjh <492795090@qq.com>
@LastEditTime: 2020-02-25 21:09:30
'''
import json, sys, os
sys.path.insert(0, os.getcwd())
from mypycorrector.rule_bert_word import rule_bert_word_corrector
ruleBertWordCorrector = rule_bert_word_corrector.RuleBertWordCorrector()

from flask import Flask, render_template, redirect, request
ruleBertWordCorrector.correct('你号')

app = Flask(__name__)
@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

@app.route("/text_correct", methods=["GET", "POST"])
def text_correct():
    return render_template('text_correct.html')

@app.route("/as_client", methods=["GET", "POST"])
def as_client():
    tar_text={}
    src_text = request.form['src_text']
    pred_sentence, pred_detail = bert_rule(src_text)
    tar_text['pred_sentence'] = pred_sentence
    tar_text['pred_detail'] = pred_detail
    return json.dumps(tar_text, ensure_ascii=False)

def bert_rule(src_text):
    pred_sentence, pred_detail = ruleBertWordCorrector.correct(src_text)
    return pred_sentence,pred_detail

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8002)