'''
@Descripttion: 
@version: 
@Author: cjh <492795090@qq.com>
@Date: 2020-02-22 13:05:23
@LastEditors: cjh <492795090@qq.com>
@LastEditTime: 2020-03-30 20:26:34
'''
import os
import sys
sys.path.insert(0, os.getcwd())
from mypycorrector.utils.io_utils import load_pkl
from mypycorrector import correct
pwd_path = os.path.abspath(os.path.dirname(__file__))
eval_result = os.path.join(pwd_path, './eval_result/eval_sighan_result.txt')
SIGHAN_CORPUS_PKL = os.path.join(pwd_path, '../../data/cn/sighan15_A2_1.pkl')
SIGHAN_CORPUS_CLEAN_TXT = os.path.join(pwd_path, '../../data/cn/sighan15_A2_clean.txt')

def dete_error_index(word_1, word_2, num):
    '''
    @Descripttion: find the index of error char
    @param {type} 
    @return: index
    '''    
    length = len(word_1)
    n=0
    for index in range(0, length):
        if (word_1[index] != word_2[index]):
            n += 1
            if (n == num):
                return index

def generate_sighan_clean(pkl_path):
    sighan_clean=open(SIGHAN_CORPUS_CLEAN_TXT,'w',encoding='utf8')
    sighan_data = load_pkl(pkl_path)
    # sighan_data=[('我想告诉妳一个东西：妳会时后，我可以帮妳买东西。请妳会家时后打给我。', [(12, '妳会时后', '妳回时候'), (14, '妳会时后', '妳回时候'), (27, '会家时后', '回家时候'), (30, '会家时后', '回家时候')])]
    for error_sentence, right_detail in sighan_data:
        sentence = list("".join(error_sentence))
        num = 0
        repeat_num=1
        before_detail = (0, "")
        for detail in right_detail:
            if detail[1] == before_detail[1] and detail[0] <= before_detail[0] + len(detail[1]):
                repeat_num += 1
                sentence.insert(detail[0] + num, '（（' + detail[2][dete_error_index(detail[1], detail[2],repeat_num)] + '））')
            else:
                repeat_num=1
                sentence.insert(detail[0] + num, '（（' + detail[2][dete_error_index(detail[1], detail[2],1)] + '））')
            before_detail = (detail[0], detail[1])
            num += 1
        sighan_clean.writelines("".join(sentence)+'\n')
    sighan_clean.close()

def eval_sighan_corpus(pkl_path, verbose=False):
    sighan_data = load_pkl(pkl_path)
    total_count = 1
    right_count = 0
    right_result = dict()
    wrong_result = dict()
    for error_sentence, right_detail in sighan_data:
        #  pred_detail: list(wrong, right, begin_idx, end_idx)
        pred_sentence, pred_detail = correct(error_sentence)
        if verbose:
            print('input sentence:', error_sentence, right_detail)
            print('pred sentence:', pred_sentence, pred_detail)
        if len(right_detail) != len(pred_detail):
            total_count += 1
        else:
            right_count += 1
    print("total_count", total_count)
    print('right_count', right_count)
    return right_count / total_count, right_result, wrong_result

if __name__ == '__main__':
    # eval_sighan_corpus(SIGHAN_CORPUS_PKL,verbose=True)
    generate_sighan_clean(SIGHAN_CORPUS_PKL)