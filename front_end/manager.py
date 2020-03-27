'''
@Descripttion: 
@version: 
@Author: cjh <492795090@qq.com>
@Date: 2020-02-24 15:22:22
@LastEditors: cjh <492795090@qq.com>
@LastEditTime: 2020-03-27 18:15:14
'''
import json, sys, os
sys.path.insert(0, os.getcwd())
from mypycorrector.rule_bert_word import rule_bert_word_corrector
from mypycorrector.bert_new import bert_corrector
ruleBertWordCorrector = rule_bert_word_corrector.RuleBertWordCorrector()
bertCorrector=bert_corrector.BertCorrector()

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
    pred_sentence, pred_detail, segments, maybe_errors = bert_rule(src_text)
    tar_text['pred_sentence'] = pred_sentence
    tar_text['pred_detail'] = pred_detail
    tar_text['segments'] = segments
    tar_text['maybe_errors'] = maybe_errors
    return json.dumps(tar_text, ensure_ascii=False)

def bert_rule(src_text):
    pred_sentence, pred_detail, segments,maybe_errors = ruleBertWordCorrector.correct(src_text)
    return pred_sentence, pred_detail, segments,maybe_errors

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8002)