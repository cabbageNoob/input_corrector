# -*- coding: UTF-8 -*-
import json
import re
import sys
import os

from mypycorrector import lm_correct_sentece
from mypycorrector import score

pwd_path = os.path.abspath(os.path.dirname(__file__))
POSTING_FILE = os.path.join(
    pwd_path, '../train/hmm/result/postinglist_final.json')


def readjson(filename):
    with open(filename, 'rb') as outfile:
        return json.load(outfile)


posting_data = readjson(POSTING_FILE)


'''判断sentence是否为拼音'''


def is_pinyin(sentence):
    return sentence.encode('utf8').isalpha()


'''判断sentence是否包含字母'''


def contain_pinyin(sentence):
    return bool(re.search('[a-z]+', sentence))


'''将拼音列表转换为汉字'''


def pinyin2hanzi(pinyin_list):
    value_hanzi_list = {}
    if len(pinyin_list) <= 2:
        path_score = sorted(posting_data[''.join(pinyin_list)].items(),
                            key=lambda x: x[1], reverse=True)
        return dict(path_score)
    else:
        i = 0
        while(2*i < len(pinyin_list)):
            pinyin_cur = ''.join(pinyin_list[2*i:2*(i+1)])
            i += 1
            path_score = dict(
                sorted(posting_data[pinyin_cur].items(), key=lambda x: x[1], reverse=True))
            value_hanzi_list.setdefault(pinyin_cur, [])
            value_hanzi_list[pinyin_cur] = path_score.keys()
        candidates = get_candidates(
            ['*'*len(''.join(pinyin_list))], value_hanzi_list)
        scores = sentence_score(candidates)
        candidate_scores = {candidate: score for candidate,
                            score in zip(candidates, scores)}
        return candidate_scores


def get_candidates(ss, value_candidate):
    for value, candidate in value_candidate.items():
        ss = [s.replace('*'*len(value), candi, 1)
              for s in ss for candi in candidate]
        ss = lm_correct_sentece(ss)
    return ss


def sentence_score(candidates):
    scores = []
    for candidate in candidates:
        scores.append(score(list(candidate)))
    return scores
