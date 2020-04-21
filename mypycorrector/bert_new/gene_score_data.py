'''
@Descripttion: 
@version: 
@Author: cjh <492795090@qq.com>
@Date: 2020-04-05 14:42:04
@LastEditors: cjh <492795090@qq.com>
@LastEditTime: 2020-04-15 10:07:12
'''
import os
import sys
sys.path.insert(0, os.getcwd())
from mypycorrector.utils.math_utils import find_all_idx
from mypycorrector.bert_new import bert_corrector
from mypycorrector.utils.neural_network_utils import Net

bertCorrector = bert_corrector.BertCorrector()
bertCorrector.enable_word_error(enable=False)

pwd_path = os.path.abspath(os.path.dirname(__file__))
sighan_2013 = os.path.join(pwd_path, '../data/cn/sighan/score_data/sighan_2013_test_new.txt')
EVAL_SIGHAN = os.path.join(pwd_path, '../data/cn/sighan15_A2_clean.txt')

score_2013_dry_path = os.path.join(pwd_path, '../data/cn/sighan/sighan_dry_test/sighan_2013_dry_test.txt')
score_2014_dry_path = os.path.join(pwd_path, '../data/cn/sighan/sighan_dry_test/sighan_2014_dry_test.txt')
score_2015_dry_path = os.path.join(pwd_path, '../data/cn/sighan/sighan_dry_test/sighan_2015_dry_test.txt')


def get_bcmi_corpus(line, left_symbol='（（', right_symbol='））'):
    """
    转换原始文本为encoder-decoder列表
    :param line: 王老师心（（性））格温和，态度和爱（（蔼）），教学有方，得到了许多人的好平（（评））。
    :param left_symbol:
    :param right_symbol:
    :return: ["王老师心格温和，态度和爱，教学有方，得到了许多人的好平。" , "王老师性格温和，态度和蔼，教学有方，得到了许多人的好评。"]
    """
    error_sentence, correct_sentence = '', ''
    # 错误词index列表
    index_list = list()
    if left_symbol not in line or right_symbol not in line:
        return line, line, index_list

    left_ids = find_all_idx(line, left_symbol)
    right_ids = find_all_idx(line, right_symbol)
    if len(left_ids) != len(right_ids):
        return error_sentence, correct_sentence,index_list
    begin = 0
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
    cnt=1
    with open(data_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            error_sentence=''
            try:
                error_sentence, right_sentence, index_list = get_bcmi_corpus(line)
            except Exception as e:
                print(e)
            if not error_sentence:
                continue
            pred_sentence, pred_detail = bertCorrector.generate_bertScore_sound_shape_file(error_sentence, right_sentence, index_list)
            
            if verbose:
                print(cnt)
                cnt+=1
        bertCorrector.score_data_file.close()


if __name__ == '__main__':
    eval_bcmi_data(sighan_2013, verbose=True)
    
            