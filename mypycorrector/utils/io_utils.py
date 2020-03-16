'''
@Descripttion: 
@version: 
@Author: cjh <492795090@qq.com>
@Date: 2020-02-20 19:42:08
@LastEditors: cjh <492795090@qq.com>
@LastEditTime: 2020-03-15 20:37:03
'''
# -*- coding: utf-8 -*-
# Author: cjh <492795090@qq.com>
# Data: 19-11-25
# Brief: 
import os
import pickle
import json
pwd_path = os.path.abspath(os.path.dirname(__file__))
SIGHAN_TXT=os.path.join(pwd_path,'../data/cn/sighan15_A2.txt')
SIGHAN_PKL=os.path.join(pwd_path,'../data/cn/sighan15_A2_1.pkl')

def load_pkl(pkl_path):
    """
    加载词典文件
    :param pkl_path:
    :return:
    """
    with open(pkl_path, 'rb') as f:
        result = pickle.load(f)
    return result


def dump_pkl(vocab, pkl_path, overwrite=True):
    """
    存储文件
    :param pkl_path:
    :param overwrite:
    :return:
    """
    if os.path.exists(pkl_path) and not overwrite:
        return
    with open(pkl_path, 'wb') as f:
        # pickle.dump(vocab, f, protocol=pickle.HIGHEST_PROTOCOL)
        pickle.dump(vocab, f, protocol=0)


def load_txt(txt_path):
    sighan_data=list()
    with open(txt_path, 'r', encoding='utf8') as file_data:
        datas = file_data.readlines()
        for line in datas[1:]:
            data=eval(line.strip())
            # data=line.strip().split(',',1)
            sighan_data.append(data)
        return sighan_data


def load_json(json_path, encoding='utf-8'):
    with open(json_path, mode='r', encoding=encoding) as json_file:
        data = json.load(json_file)
    return data


def save_json(data, json_path, mode='w', encoding='utf-8'):
    dir = os.path.dirname(os.path.abspath(json_path))
    if not os.path.exists(dir):
        print(dir)
        os.makedirs(dir)
    with open(json_path, mode=mode, encoding=encoding) as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=4))


if __name__ == '__main__':
    sighan_data = load_txt(SIGHAN_TXT)
    dump_pkl(sighan_data, SIGHAN_PKL)
    

