'''
@Descripttion: 
@version: 
@Author: cjh <492795090@qq.com>
@Date: 2020-02-24 15:22:22
@LastEditors: cjh <492795090@qq.com>
@LastEditTime: 2020-04-21 10:56:32
'''
import json, sys, os
sys.path.insert(0, os.getcwd())
from mypycorrector.rule_bert_word import rule_bert_word_corrector
ruleBertWordCorrector = rule_bert_word_corrector.RuleBertWordCorrector()

from flask import Flask, render_template, redirect, request
# ruleBertWordCorrector.correct('你号')

from mypycorrector.utils.neural_network_utils import Net

# bertCorrector.enable_word_error(enable = False)
from mypycorrector.bert_new.bert_multi_thread import multi_threads_correct

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
    pred_sentence, pred_detail = multi_threads_correct(src_text)
    tar_text['pred_sentence'] = pred_sentence
    tar_text['pred_detail'] = pred_detail
    # tar_text['segments'] = segments
    # tar_text['maybe_errors'] = maybe_errors
    return json.dumps(tar_text, ensure_ascii=False)

def bert_rule(src_text):
    pred_sentence, pred_detail, segments,maybe_errors = ruleBertWordCorrector.correct(src_text)
    return pred_sentence, pred_detail, segments,maybe_errors

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8002)