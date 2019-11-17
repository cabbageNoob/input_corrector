# -*- coding: utf-8 -*-
# Author: XuMing <xuming624@qq.com>
# Brief:
import re
from codecs import open
from pycorrector import correct
from pycorrector.utils.io_utils import load_pkl
from pycorrector.utils.math_utils import find_all_idx


def get_bcmi_corpus(line, left_symbol='（（', right_symbol='））'):
    """
    转换原始文本为encoder-decoder列表
    :param line: 王老师心（（性））格温和，态度和爱（（蔼）），教学有方，得到了许多人的好平（（评））。
    :param left_symbol:
    :param right_symbol:
    :return: ["王老师心格温和，态度和爱，教学有方，得到了许多人的好平。" , "王老师性格温和，态度和蔼，教学有方，得到了许多人的好评。"]
    """
    error_sentence, correct_sentence = '', ''
    if left_symbol not in line or right_symbol not in line:
        return error_sentence, correct_sentence

    left_ids = find_all_idx(line, left_symbol)
    right_ids = find_all_idx(line, right_symbol)
    if len(left_ids) != len(right_ids):
        return error_sentence, correct_sentence
    begin = 0
    #错误词index列表
    index_list=list()
    index = line.find('（（')
    while (index != -1):
        index_list.append(index - 5*len(index_list)-1)
        index = line.find('（（', index + 1)
    for left, right in zip(left_ids, right_ids):
        correct_len = right - left - len(left_symbol)
        correct_word = line[(left + len(left_symbol)):right]
        error_sentence += line[begin:left]
        correct_sentence += line[begin:(left - correct_len)] + correct_word
        begin = right + len(right_symbol)
    error_sentence += line[begin:]
    correct_sentence += line[begin:]
    return error_sentence, correct_sentence, index_list


def eval_bcmi_data(data_path, verbose=False):
    sentence_size = 1
    right_count = 0
    right_result = dict()
    wrong_result = dict()
    #其他数据
    word_count=0
    word_detec_count=0
    word_detec_count_char=0#预测出字的数目
    word_detec_index_right=0#预测位置正确
    word_right=0
    word_wrong=0
    word_forget=0
    word_wrong_add=0#误杀
    with open(data_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            try:
                error_sentence, right_sentence,index_list = get_bcmi_corpus(line)
            except Exception as e:
                print(e)
            if not error_sentence:
                continue
            pred_sentence, pred_detail = correct(error_sentence)
            if verbose:
                print('input sentence:', error_sentence)
                print('pred sentence:', pred_sentence, pred_detail)
                print('right sentence:', right_sentence)
                print('wrong_index', index_list)
            sentence_size += 1
            word_count+=len(index_list)
            word_detec_count+=len(pred_detail)#预判错误个数
            #预测的错误字词
            pred_index_list=list()
            for detail in pred_detail:
                if len(detail[0])==1:
                    word_detec_count_char+=1
                temp=detail[2]
                while(temp<detail[3]):
                    pred_index_list.append(temp)
                    temp+=1

            for i,index in enumerate(index_list):
                if index in pred_index_list:
                    word_detec_index_right+=1
                    if(pred_sentence[index]==right_sentence[index]):
                        word_right+=1#词预测正确
                    else:
                        word_wrong+=1
            #遗漏词
            word_forget=word_count-word_detec_index_right
            #误杀误判词
            word_wrong_add=word_detec_count-word_detec_index_right


            if right_sentence == pred_sentence:
                right_count += 1
                right_result[error_sentence] = [right_sentence, pred_sentence]
            else:
                wrong_result[error_sentence] = [right_sentence, pred_sentence]
    if verbose:
        print('right count:', right_count, ';sentence size:', sentence_size)
        print('词错误数量:',word_count, ';预判字词错误总数量:',word_detec_count)
        print('预测出错字数目:',word_detec_count_char,'预测出错词数目:',word_detec_count-word_detec_count_char)
        print('预测错误词位置正确数目: ',word_detec_index_right)
        print('准确预测错误，并成功纠错数目:',word_right)
        print('准确预测错误，但纠错失败:', word_wrong)
        print('错误词遗漏数: ',word_forget)
        print('误杀误判词数',word_wrong_add)

    return right_count / sentence_size, right_result, wrong_result


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
    print("total_count",total_count)
    print('right_count',right_count)
    return right_count / total_count, right_result, wrong_result


#-----------------test----------------
def eval_sighan_corpus_test(pkl_path, verbose=False):
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
        total_count += 1
        if len(right_detail) != len(pred_detail):
            continue
            # total_count += 1
        else:
            right_count += 1
    print("total_count", total_count)
    print('right_count', right_count)
    return right_count / total_count, right_result, wrong_result

if __name__ == "__main__":
    # lst = ['少先队员因（（应））该为老人让坐（（座））。',
    #        '王老师心（（性））格温和，态度和爱（（蔼）），教学有方，得到了许多人的好平（（评））。',
    #        '青蛙是庄家的好朋友，我们要宝（（保））护它们。']
    # for i in lst:
    #     print(get_bcmi_corpus(i))

    ringht_rate, right_result, wrong_result=eval_bcmi_data(r'D:\testFile\pycorrector\pycorrector\data\cn\bcmi.txt',verbose=True)
    # print("right_count / total_count",ringht_rate)
    # print("right_result",right_result)
    # print("wrong_result",wrong_result)
    # eval_sighan_corpus_test(r"D:\testFile\pycorrector\pycorrector\data\cn\sighan15_A2.pkl",verbose=True)
    index_list=list()
    test_str='王老师心（（性））格温和，态度和爱（（蔼）），教学有方，得到了许多人的好平（（评））。'
    index=test_str.find('（（')
    while(index!=-1):
        index_list.append(index-5*len(index_list)-1)
        index=test_str.find('（（',index+1)
    print(index_list)