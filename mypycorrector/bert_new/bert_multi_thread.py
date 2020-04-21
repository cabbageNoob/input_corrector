'''
@Descripttion: 
@version: 
@Author: cjh <492795090@qq.com>
@Date: 2020-04-19 22:12:20
@LastEditors: cjh <492795090@qq.com>
@LastEditTime: 2020-04-21 10:51:04
'''
import sys, os
sys.path.insert(0, os.getcwd())
from mypycorrector.bert_new import bert_corrector
from mypycorrector.utils.text_utils import is_chinese_string, convert_to_unicode
from mypycorrector.utils.text_utils import uniform, is_alphabet_string
from mypycorrector.utils.neural_network_utils import Net

bertCorrector = bert_corrector.BertCorrector()
# bertCorrector.enable_word_error(enable = False)
bertCorrector.check_corrector_initialized()
bertCorrector.check_detector_initialized()

import time

from threading import Thread

class MyThread(Thread):

    def __init__(self, text,start_idx):
        Thread.__init__(self)
        self.text = text
        self.start_idx = start_idx

    def run(self):
        self.pred_text, self.pred_details = bertCorrector.correct_short(self.text, self.start_idx)
        
    def get_result(self):
        return self.pred_text, self.pred_details

def multi_threads_correct(text):
    threads_list = []
    text_new = ''
    details=[]
    # 编码统一，utf-8 to unicode
    test = convert_to_unicode(text)
    blocks = bertCorrector.split_2_short_text(text, include_symbol=True)
    for blk, start_idx in blocks:
        threads_list.append(MyThread(blk, start_idx))
    for thread in threads_list:
        thread.start()
        # thread.join()
        # pred_text,pred_details=thread.get_result()
        # text_new += pred_text
        # for detail in pred_details:
        #     details.append(detail)
    for thread in threads_list:
        thread.join()
        pred_text,pred_details=thread.get_result()
        text_new += pred_text
        for detail in pred_details:
            details.append(detail)
    return text_new, details
    

if __name__ == '__main__':
    test = '令天突然冷了起来，妈妈丛相子里番出一件旧棉衣让我穿上。我不原意。在妈妈得说服叫育下，我中于穿上哪件棉衣哼着哥儿上学去了。'
    test = '今天我在菜园里抓到一只蝴'
    test = '在北京京的生活节奏奏是很快的'
    t1 = time.time()
    text_new, details = multi_threads_correct(test)
    print(text_new, details)
    print('multi threads spend {}'.format(time.time() - t1))
    
    
    t1 = time.time()
    pred_text, pred_details = bertCorrector.bert_correct_ssc(test)
    print(pred_text, pred_details)
    print('single thread spends {}'.format(time.time() - t1))
    
    
    t1 = time.time()
    pred_text, pred_details = bertCorrector.bert_correct_ssc_origin(test)
    print(pred_text, pred_details)
    print('origin spends {}'.format(time.time() - t1))
