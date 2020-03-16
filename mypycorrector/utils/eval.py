'''
@Descripttion: 
@version: 
@Author: cjh <492795090@qq.com>
@Date: 2020-03-15 20:17:38
@LastEditors: cjh <492795090@qq.com>
@LastEditTime: 2020-03-15 21:00:10
'''
import copy
import os
import sys
from codecs import open
from random import sample
from xml.dom import minidom
sys.path.insert(0, os.getcwd())
from mypycorrector.utils.io_utils import load_json, save_json
from mypycorrector.utils.io_utils import load_pkl
from mypycorrector.utils.math_utils import find_all_idx
pwd_path = os.path.abspath(os.path.dirname(__file__))
eval_data_path = os.path.join(pwd_path, '../data/eval_cged_corpus.json')


def build_cged_corpus(data_path_list, output_path, limit_size=500):
    corpus = []
    for data_path in data_path_list:
        print('Parse data from %s' % data_path)
        dom_tree = minidom.parse(data_path)
        docs = dom_tree.documentElement.getElementsByTagName('DOC')
        count = 0
        for doc in docs:
            # Input the text
            text = doc.getElementsByTagName('TEXT')[0]. \
                childNodes[0].data.strip()
            # Input the correct text
            correction = doc.getElementsByTagName('CORRECTION')[0]. \
                childNodes[0].data.strip()

            if correction:
                count += 1
                line_dict = {"text": text, "correction": correction, "errors": []}
                corpus.append(line_dict)
                # if count > limit_size:
                #     break
        print(count)
    save_json(corpus, output_path)


def build_eval_corpus():
    cged_path_16 = os.path.join(pwd_path, '../data/cn/CGED/CGED16_HSK_TrainingSet.xml')
    cged_path_17 = os.path.join(pwd_path, '../data/cn/CGED/CGED17_HSK_TrainingSet.xml')
    cged_path_18 = os.path.join(pwd_path, '../data/cn/CGED/CGED18_HSK_TrainingSet.xml')

    cged_path_list = [cged_path_16, cged_path_17, cged_path_18]
    build_cged_corpus(cged_path_list, eval_data_path)
    # char_errors = load_json(char_error_path)

if __name__ == '__main__':
    build_eval_corpus()

