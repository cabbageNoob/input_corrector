'''
@Descripttion: 
@version: 
@Author: cjh <492795090@qq.com>
@Date: 2020-02-24 15:22:22
@LastEditors: cjh <492795090@qq.com>
@LastEditTime: 2020-02-24 20:52:23
'''
import json
from flask import Flask, render_template, redirect, request
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
    print(src_text)
    tar_text['tar_text']=src_text
    
    return json.dumps(tar_text, ensure_ascii=False)

if __name__ == '__main__':
    app.run(host='127.0.0.1',port=8002)