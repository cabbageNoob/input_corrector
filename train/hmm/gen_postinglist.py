# coding: utf-8
# Author: cjh<492795090@qq.com>
# Date: 19-12-01
import sys
import json

from Pinyin2Hanzi import DefaultHmmParams
from Pinyin2Hanzi import viterbi
from Pinyin2Hanzi import cut

from Pinyin2Hanzi.pinyincut import Trie
from Pinyin2Hanzi.pinyincut import TrieNode

sys.path = ['../..'] + sys.path
from Pinyin2Hanzi import util

PINYIN_FILE        ='./result/all_pinyin.txt'

POSTING_LIST       ='./result/postinglist.json'

def writejson2file(data, filename):
    with open(filename, 'w',encoding='utf8') as outfile:
        data = json.dumps(data, indent=4, sort_keys=True, ensure_ascii=False)
        outfile.write(data)

def readjson(filename):
    with open(filename,'rb') as outfile:
        return json.load(outfile)

def read_from_all_pinyin(all_pinyin):
    print("begin read from all_pinyin.txt")
    for line in open(PINYIN_FILE, encoding='utf8'):
        line = util.as_text(line.strip())
        all_pinyin.append(line)

def process_postinglist(all_pinyin,posting_list):
    print('begin process posting_list')
    for _one in all_pinyin:
        print(all_pinyin.index(_one))
        for _two in all_pinyin:
            posting_list.setdefault(_one+_two,{})
            posting_list[_one+_two]=gen_pinyin2hanzi(tuple([_one,_two]))

#result:
#{'你好':score,'':score,...}
def gen_pinyin2hanzi(pinyin,num=5):
    results={}
    hmmparams = DefaultHmmParams()
    result = viterbi(hmm_params=hmmparams, observations=pinyin, path_num=num, log=True)
    for item in result:
        # results.setdefault(''.join(item.path),0)
        results[''.join(item.path)]=item.score
    return results

def delete_posting(data):
    print("delete......")
    for pinyin in list(data.keys()):
        if(len(cut(pinyin))!=2):
            data.pop(pinyin)

def add_posting(data,all_pinyin):
    print('add ......')
    for _one in all_pinyin:
        print(all_pinyin.index(_one))
        data.setdefault(_one,{})
        data[_one]=gen_pinyin2hanzi(tuple([_one,]))

def gen_postinglist():
    all_pinyin=[]
    posting_list={}     # 倒排列表  格式应该为{'nihao':{'你好':score,'':score,...}}

    read_from_all_pinyin(all_pinyin)
    process_postinglist(all_pinyin,posting_list)

    delete_posting(posting_list)
    add_posting(posting_list, all_pinyin)
    #write json
    writejson2file(posting_list, POSTING_LIST)


def main():
    gen_postinglist()

if __name__ == '__main__':
    # main()
    data=readjson('./result/postinglist_final.json')
    for pinyin,path_score in data.items():
        path_score=sorted(path_score.items(),key=lambda x:x[1],reverse=True)
        data[pinyin]=dict(path_score)
        # print(data[pinyin])
    writejson2file(data, './result/postinglist_final_1.json')
