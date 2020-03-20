'''
@Descripttion: use bert detect and correct chinese char error
@version: 
@Author: cjh (492795090@qq.com)
@Date: 2020-03-18 07:33:36
@LastEditors: cjh <492795090@qq.com>
@LastEditTime: 2020-03-20 20:31:24
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


class BertCorrector(Corrector):
    def __init__(self, bert_model_dir=config.bert_model_dir,
                 bert_config_path=config.bert_config_path,
                 bert_model_path=config.bert_model_path):
                #  bert_config_path='../data/bert_models/chinese_finetuned_lm/config.json',
                #  bert_model_path='../data/bert_models/chinese_finetuned_lm/pytorch_model.bin'):

        super(BertCorrector, self).__init__()
        self.name = 'bert_corrector'
        t1 = time.time()
        self.model = pipeline('fill-mask',
                              model=bert_model_path,
                              config=bert_config_path,
                              tokenizer=bert_model_dir)
        if self.model:
            self.mask = self.model.tokenizer.mask_token
            logger.debug('Loaded bert model: %s, spend: %.3f s.' % (bert_model_dir, time.time() - t1))

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
        # 长句切分为短句
        blocks = self.split_2_short_text(text, include_symbol=True)
        for blk, start_idx in blocks:
            blk_new = ''
            for idx, s in enumerate(blk):
                # 对非中文的错误不做处理
                if is_chinese_string(s):
                    sentence_lst = list(blk)
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
                                    details.append([s, token_str, idx, idx + 1])
                                    s = token_str
                                    break
                blk_new += s
            text_new += blk_new
        details = sorted(details, key=operator.itemgetter(2))
        return text_new, details


if __name__ == "__main__":
    d = BertCorrector()
    error_sentences = [
        '少先队员因该为老人让坐',
        '少 先  队 员 因 该 为 老人让坐',
        '机七学习是人工智能领遇最能体现智能的一个分知',
        '今天心情很好',
    ]
    for sent in error_sentences:
        corrected_sent, err = d.bert_correct(sent)
        print("original sentence:{} => {}, err:{}".format(sent, corrected_sent, err))
