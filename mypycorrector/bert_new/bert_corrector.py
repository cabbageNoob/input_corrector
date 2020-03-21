'''
@Descripttion: use bert detect and correct chinese char error
@version: 
@Author: cjh (492795090@qq.com)
@Date: 2020-03-18 07:33:36
@LastEditors: cjh <492795090@qq.com>
@LastEditTime: 2020-03-21 20:13:44
'''
# -*- coding: utf-8 -*-
import operator
import sys,os
import time

from transformers import pipeline
pwd_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append('../..')
sys.path.insert(0,os.getcwd())
from mypycorrector.bert_new import config
from mypycorrector.utils.text_utils import is_chinese_string, convert_to_unicode
from mypycorrector.utils.logger import logger
from mypycorrector.corrector import Corrector
from mypycorrector.detector import ErrorType
from mypycorrector.bert_new.bert_detector import BertDetector


class BertCorrector(Corrector):
    def __init__(self, bert_model_dir=config.bert_model_dir,
                 bert_config_path=config.bert_config_path,
                 bert_model_path=config.bert_model_path):
                #  bert_config_path='../data/bert_models/chinese_finetuned_lm/config.json',
                #  bert_model_path='../data/bert_models/chinese_finetuned_lm/pytorch_model.bin'):

        super(BertCorrector, self).__init__()
        self.name = 'bert_corrector'
        self.bertDetector=BertDetector()
        t1 = time.time()
        self.model = pipeline('fill-mask',
                              model=bert_model_path,
                              config=bert_config_path,
                              tokenizer=bert_model_dir)
        if self.model:
            self.mask = self.model.tokenizer.mask_token
            logger.debug('Loaded bert model: %s, spend: %.3f s.' % (bert_model_dir, time.time() - t1))

    @staticmethod
    def _check_contain_details_error(maybe_err, details):
        """
        检测错误集合(details)是否已经包含该错误位置（maybe_err)
        :param maybe_err: [error_word, begin_pos, end_pos, error_type]
        :param maybe_errors:[error_word, correct_word, begin_pos, end_pos, error_type]
        :return:
        """
        for detail in details:
            if maybe_err[0] in detail[0] and maybe_err[1] >= detail[2] and \
                    maybe_err[2] <= detail[3]:
                return True
        return False

    def generate_items_word_char(self, char, before_sent, after_sent, begin_idx, end_idx):
        '''
        @Descripttion: 生成可能多字少字误字的候选集
        @param {type} 
        @return: 
        '''   
        candidates_1_order = []
        candidates = []
        # same pinyin word
        candidates_1_order.extend(self._confusion_word_set(char))
        # custom confusion word
        candidates_1_order.extend(self._confusion_custom_set(char))
        candidates.extend(candidates_1_order)
        # same one char pinyin
        confusion = self._confusion_char_set(char)
        candidates.extend(confusion)
        candidates = [(i, ErrorType.word) for i in candidates]
        # multi char
        candidates.append(('',ErrorType.redundancy))
        # miss char
        sentence = before_sent + self.mask + char + after_sent
        corrected_item_idx = self.model(sentence)[0].get('token', 0)
        corrected_item=self.model.tokenizer.convert_ids_to_tokens(corrected_item_idx)
        candidates.append((corrected_item + char, ErrorType.miss))

        sentence = before_sent + char + self.mask + after_sent
        corrected_item_idx = self.model(sentence)[0].get('token', 0)
        corrected_item=self.model.tokenizer.convert_ids_to_tokens(corrected_item_idx)
        candidates.append((char + corrected_item, ErrorType.miss))
        return candidates
    
    def bert_correct(self, text):
        """
        句子纠错
        :param text: 句子文本
        :return: list[list], [error_word, begin_pos, end_pos, error_type]
        """
        text_new = ''
        details = []
        self.check_corrector_initialized()
        # 编码统一，utf-8 to unicode
        text = convert_to_unicode(text)
        if self.enable_word_error:
            maybe_errors = self.bertDetector.detect(text)
            # trick: 类似翻译模型，倒序处理
            maybe_errors = sorted(maybe_errors, key=operator.itemgetter(2), reverse=True)
            for cur_item, begin_idx, end_idx, err_type in maybe_errors:
                # 纠错，逐个处理
                before_sent = text[:begin_idx]
                after_sent = text[end_idx:]

                # 对非中文的错字不做处理
                if not is_chinese_string(cur_item):
                    continue
                # 困惑集中指定的词，直接取结果
                if err_type == ErrorType.confusion:
                    corrected_item = (self.custom_confusion[cur_item], ErrorType.confusion)
                # 对碎片且不常用单字，可能错误是多字少字
                elif err_type == ErrorType.word_char:
                    maybe_right_items = self.generate_items_word_char(cur_item, before_sent, after_sent, begin_idx, end_idx)
                    corrected_item = self.lm_correct_item(cur_item, maybe_right_items, before_sent, after_sent)
                # 多字
                elif err_type == ErrorType.redundancy:
                    maybe_right_items = [('',ErrorType.redundancy)]
                    corrected_item = self.lm_correct_item(cur_item, maybe_right_items, before_sent, after_sent)
                elif err_type == ErrorType.word:
                    # 取得所有可能正确的词
                    candidates = self.generate_items(cur_item)
                    if not candidates:
                        continue
                    candidates=[(item,ErrorType.word) for item in candidates]
                    corrected_item = self.lm_correct_item(cur_item, candidates, before_sent, after_sent)
                    # 对ErrorType.word错误进行双层检测
                    # 对多字词进行处理
                    if len(corrected_item[0]) > 2 and corrected_item[0] not in self.word_freq:
                        candidates = self.generate_items_for_word(corrected_item[0])
                        if not candidates:
                            continue
                        candidates=[(item,ErrorType.word) for item in candidates]
                        corrected_item = self.lm_correct_item(corrected_item[0], candidates, before_sent, after_sent)
    
                # output
                if corrected_item[0] != cur_item:
                    text = before_sent + corrected_item[0] + after_sent
                    detail_word = [cur_item, corrected_item[0], begin_idx, end_idx, corrected_item[1]]
                    details.append(detail_word)

        if self.enable_char_error:
            text_new = ""
            for idx, s in enumerate(text):
                # 对非中文的错误不做处理
                if is_chinese_string(s):
                    # 对已包含错误不处理
                    maybe_err = [s, idx, idx + 1, ErrorType.char]
                    if not self._check_contain_details_error(maybe_err, details):
                        sentence_lst = list(text_new + text[idx:])
                        sentence_lst[idx] = self.mask
                        sentence_new = ''.join(sentence_lst)
                        predicts = self.model(sentence_new)
                        top_tokens = []
                        for p in predicts:
                            token_id = p.get('token', 0)
                            token_str = self.model.tokenizer.convert_ids_to_tokens(token_id)
                            top_tokens.append(token_str)

                        if top_tokens and (s not in top_tokens):
                            # 取得所有可能正确的词
                            candidates = self.generate_items(s)
                            if candidates:
                                for token_str in top_tokens:
                                    if token_str in candidates:
                                        details.append([s, token_str, idx, idx + 1,ErrorType.char])
                                        s = token_str
                                        break
                text_new += s

        details = sorted(details, key=operator.itemgetter(2))
        return text_new, details


if __name__ == "__main__":
    d = BertCorrector()
    error_sentences = [
        '今天我在菜园里抓到一只蝴',
        '少先队员因该为老人让坐',
        '少 先  队 员 因 该 为 老人让坐',
        '机七学习是人工智能领遇最能体现智能的一个分知',
        '今天心情很好',
    ]
    for sent in error_sentences:
        corrected_sent, err = d.bert_correct(sent)
        print("original sentence:{} => {}, err:{}".format(sent, corrected_sent, err))
