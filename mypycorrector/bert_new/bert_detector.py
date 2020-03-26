'''
@Descripttion: 
@version: 
@Author: cjh <492795090@qq.com>
@Date: 2020-03-21 14:41:45
@LastEditors: cjh <492795090@qq.com>
@LastEditTime: 2020-03-21 20:07:46
'''
import operator
import sys,os
import time

from transformers import pipeline
pwd_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append('../..')
sys.path.insert(0,os.getcwd())
from mypycorrector.bert_new import config
from mypycorrector.utils.text_utils import is_chinese_string, convert_to_unicode
from mypycorrector.utils.text_utils import uniform, is_alphabet_string
from mypycorrector.utils.logger import logger
from mypycorrector.detector import Detector
from mypycorrector.detector import ErrorType


class BertDetector(Detector):
    def __init__(self):
        super(BertDetector, self).__init__()
        self.name = 'bert_detector'

    def detect(self, sentence):
        """
        检测句子中的疑似错误信息，包括[词、位置、错误类型]
        :param text:
        :return: list[list], [error_word, begin_pos, end_pos, error_type]
        """
        maybe_errors = []
        if not sentence.strip():
            return maybe_errors
        # 初始化
        self.check_detector_initialized()
        # 编码统一，utf-8 to unicode
        sentence = convert_to_unicode(sentence)
        # 文本归一化
        sentence = uniform(sentence)
        # 切词
        tokens = self.tokenizer.tokenize(sentence)
        
        # 自定义混淆集加入疑似错误词典
        for confuse in self.custom_confusion:
            idx = sentence.find(confuse)
            if idx > -1:
                maybe_err = [confuse, idx + start_idx, idx + len(confuse) + start_idx, ErrorType.confusion]
                self._add_maybe_error_item(maybe_err, maybe_errors, ErrorType.confusion)
        
        if self.is_word_error_detect:
            # 未登录词加入疑似错误词典
            for word, begin_idx, end_idx in tokens:
                # pass filter word
                if self.is_filter_token(word):
                    continue
                # pass in dict
                if word in self.word_freq:
                    # 多字词或词频大于50000的单字，可以continue
                    if len(word) == 1 and word in self.char_freq and self.char_freq.get(word) < 50000:                                  
                        maybe_err = [word, begin_idx, end_idx, ErrorType.word_char]
                        self._add_maybe_error_item(maybe_err, maybe_errors)
                        continue
                    # 出现叠字，考虑是否多字
                    if len(word) == 1 and sentence[begin_idx - 1] == word:
                        maybe_err = [word, begin_idx, end_idx, ErrorType.redundancy]
                        self._add_maybe_error_item(maybe_err, maybe_errors)
                    continue
                
                # 对碎片单字进行检测，可能多字、少字、错字
                if len(word) == 1:
                    maybe_err = [word, begin_idx, end_idx, ErrorType.word_char]
                    self._add_maybe_error_item(maybe_err, maybe_errors)
                    continue
                maybe_err = [word, begin_idx, end_idx, ErrorType.word]
                self._add_maybe_error_item(maybe_err, maybe_errors)
        return sorted(maybe_errors, key=lambda k: k[1], reverse=False)


