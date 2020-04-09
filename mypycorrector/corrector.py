# -*- coding: utf-8 -*-
'''
@Descripttion: corrector with spell and stroke
@version: 
@Author: cjh <492795090@qq.com>
@Date: 2019-12-19 14:12:17
@LastEditors: cjh <492795090@qq.com>
@LastEditTime: 2020-04-09 19:02:02
'''
import codecs
import operator
import os, sys
import time
from math import pow

from pypinyin import lazy_pinyin
sys.path.insert(0,os.getcwd())
from mypycorrector import config
from mypycorrector.detector import Detector, ErrorType
from mypycorrector.utils.logger import logger
from mypycorrector.utils.math_utils import edit_distance_word
from mypycorrector.utils.text_utils import is_chinese_string
from mypycorrector.bert.bert_corrector import BertCorrector


def load_char_set(path):
    words = set()
    with codecs.open(path, 'r', encoding='utf-8') as f:
        for w in f:
            words.add(w.strip())
    return words

def load_same_pinyin(path, sep='\t'):
    """
    加载同音字
    :param path:
    :param sep:
    :return:
    """
    result = dict()
    if not os.path.exists(path):
        logger.warn("file not exists:" + path)
        return result
    with codecs.open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('#'):
                continue
            parts = line.split(sep)
            if parts and len(parts) > 2:
                key_char = parts[0]
                # same_pron_same_tone = set(list(parts[1]))
                # same_pron_diff_tone = set(list(parts[2]))
                # value = same_pron_same_tone.union(same_pron_diff_tone)
                value=set()
                for part in parts[1:]:
                    value=value.union(set(list(part)))
                if len(key_char) > 1 or not value:
                    continue
                result[key_char] = value
    return result

def load_same_stroke(path, sep='\t'):
    """
    加载形似字
    :param path:
    :param sep:
    :return:
    """
    result = dict()
    if not os.path.exists(path):
        logger.warn("file not exists:" + path)
        return result
    with codecs.open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('#'):
                continue
            parts = line.split(sep)
            if parts and len(parts) > 1:
                # for i, c in enumerate(parts):
                #     result[c] = set(list(parts[:i] + parts[i + 1:]))
                result[parts[0]] = set(list(parts[1]))
    return result


class Corrector(Detector):
    def __init__(self, common_char_path=config.common_char_path,
                 same_pinyin_path=config.same_pinyin_path,
                 same_stroke_path=config.same_stroke_path,
                 language_model_path=config.language_model_path,
                 word_freq_path=config.word_freq_path,
                 custom_word_freq_path=config.custom_word_freq_path,
                 custom_confusion_path=config.custom_confusion_path,
                 person_name_path=config.person_name_path,
                 place_name_path=config.place_name_path,
                 stopwords_path=config.stopwords_path):
        super(Corrector, self).__init__(language_model_path=language_model_path,
                                        word_freq_path=word_freq_path,
                                        custom_word_freq_path=custom_word_freq_path,
                                        custom_confusion_path=custom_confusion_path,
                                        person_name_path=person_name_path,
                                        place_name_path=place_name_path,
                                        stopwords_path=stopwords_path)
        self.name = 'corrector'
        self.common_char_path = common_char_path
        self.same_pinyin_text_path = same_pinyin_path
        self.same_stroke_text_path = same_stroke_path
        self.bert_corrector = BertCorrector()
        self.initialized_corrector = False

    def initialize_corrector(self):
        t1 = time.time()
        # chinese common char dict
        self.cn_char_set = load_char_set(self.common_char_path)
        # same pinyin
        self.same_pinyin = load_same_pinyin(self.same_pinyin_text_path)
        # same stroke
        self.same_stroke = load_same_stroke(self.same_stroke_text_path)
        logger.debug("Loaded same pinyin file: %s, same stroke file: %s, spend: %.3f s." % (
            self.same_pinyin_text_path, self.same_stroke_text_path, time.time() - t1))
        # self.bert_corrector.check_bert_detector_initialized()
        self.initialized_corrector = True

    def check_corrector_initialized(self):
        if not self.initialized_corrector:
            self.initialize_corrector()

    def get_same_pinyin(self, char):
        """
        取同音字
        :param char:
        :return:
        """
        self.check_corrector_initialized()
        return self.same_pinyin.get(char, set())

    def get_same_stroke(self, char):
        """
        取形似字
        :param char:
        :return:
        """
        self.check_corrector_initialized()
        return self.same_stroke.get(char, set())

    def known(self, words):
        """
        取得词序列中属于常用词部分
        :param words:
        :return:
        """
        self.check_detector_initialized()
        return set(word for word in words if word in self.word_freq)

    def _confusion_char_set(self, c):
        return self.get_same_pinyin(c).union(self.get_same_stroke(c))

    def _confusion_word_set(self, word):
        confusion_word_set = set()
        candidate_words = list(self.known(edit_distance_word(word, self.cn_char_set)))
        for candidate_word in candidate_words:
            if lazy_pinyin(candidate_word) == lazy_pinyin(word):
                # same pinyin
                confusion_word_set.add(candidate_word)
        return confusion_word_set

    def _confusion_custom_set(self, word):
        confusion_word_set = set()
        if word in self.custom_confusion:
            confusion_word_set = {self.custom_confusion[word]}
        return confusion_word_set

    # TODO: need more faster
    def generate_items(self, word, fraction=1):
        """
        生成纠错候选集
        :param word:
        :param fraction:
        :return:
        """
        self.check_corrector_initialized()
        candidates_1_order = []
        candidates_2_order = []
        candidates_3_order = []
        # same pinyin word
        candidates_1_order.extend(self._confusion_word_set(word))
        # custom confusion word
        candidates_1_order.extend(self._confusion_custom_set(word))
        # same pinyin char
        if len(word) == 1:
            # same one char pinyin
            confusion = [i for i in self._confusion_char_set(word[0]) if i]
            candidates_1_order.extend(confusion)
        if len(word) == 2:
            # same first char pinyin
            confusion = [i + word[1:] for i in self._confusion_char_set(word[0]) if i]
            candidates_2_order.extend(confusion)
            # same last char pinyin
            confusion = [word[:-1] + i for i in self._confusion_char_set(word[-1]) if i]
            candidates_2_order.extend(confusion)
        if len(word) > 2:
            # same mid char pinyin
            confusion = [word[0] + i + word[2:] for i in self._confusion_char_set(word[1])]
            candidates_3_order.extend(confusion)

            # same first word pinyin
            confusion_word = [i + word[-1] for i in self._confusion_word_set(word[:-1])]
            candidates_3_order.extend(confusion_word)

            # same last word pinyin
            confusion_word = [word[0] + i for i in self._confusion_word_set(word[1:])]
            candidates_3_order.extend(confusion_word)

        # add all confusion word list
        confusion_word_set = set(candidates_1_order + candidates_2_order + candidates_3_order)
        confusion_word_list = [item for item in confusion_word_set if is_chinese_string(item)]
        confusion_sorted = sorted(confusion_word_list, key=lambda k: self.word_frequency(k), reverse=True)
        return confusion_sorted[:len(confusion_word_list) // fraction + 1]

    def generate_items_for_word(self, word, fraction=1):
        candidates_1_order = []
        candidates_2_order = []
        candidates_3_order = []
        # same pinyin word
        candidates_1_order.extend(self._confusion_word_set(word))
        # custom confusion word
        candidates_1_order.extend(self._confusion_custom_set(word))
        if len(word) == 2:
            # same first char pinyin
            confusion = [i + word[1:] for i in self._confusion_char_set(word[0]) if i]
            candidates_2_order.extend(confusion)
            # same last char pinyin
            confusion = [word[:-1] + i for i in self._confusion_char_set(word[-1]) if i]
            candidates_2_order.extend(confusion)
        if len(word) > 2:
            # same first char pinyin
            confusion = [i + word[1:] for i in self._confusion_char_set(word[0]) if i]
            candidates_3_order.extend(confusion)
            # same last char pinyin
            confusion = [word[:-1] + i for i in self._confusion_char_set(word[-1]) if i]
            candidates_3_order.extend(confusion)
        # add all confusion word list
        confusion_word_set = set(candidates_1_order + candidates_2_order + candidates_3_order)
        confusion_word_list = [item for item in confusion_word_set if is_chinese_string(item)]
        confusion_sorted = sorted(confusion_word_list, key=lambda k: self.word_frequency(k), reverse=True)
        return confusion_sorted[:len(confusion_word_list) // fraction + 1]
    
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
        corrected_item = self.predict_mask_token_(before_sent + '*' + char + after_sent, begin_idx, begin_idx + 1)
        candidates.append((corrected_item + char, ErrorType.miss))
        corrected_item = self.predict_mask_token_(before_sent + char + '*' + after_sent, end_idx, end_idx + 1)
        candidates.append((char + corrected_item, ErrorType.miss))
        return candidates

    def lm_correct_item(self, item, maybe_right_items, before_sent, after_sent):
        """
        通过语音模型纠正字词错误
        """
        import heapq
        if item not in maybe_right_items:
            maybe_right_items.append((item,'itself'))
        corrected_item = min(maybe_right_items, key=lambda k: self.ppl_score(list(before_sent + k[0] + after_sent)))
        # corrected_items=heapq.nsmallest(5,maybe_right_items,key=lambda k: self.ppl_score(list(before_sent + k + after_sent)))
        return corrected_item

    def lm_correct_sentece(self, sentences_list):
        """
        通过语言模型获取最有可能正确的句子
        :param sentences_list:
        :return: sentences_list
        """
        import heapq
        sentences_list=heapq.nlargest(5,sentences_list,key=lambda sentence: self.score(list(sentence)))
        return sentences_list

    def correct(self, sentence, reverse=True):
        """
        句子改错
        :param sentence: 句子文本
        :return: 改正后的句子, list(wrong, right, begin_idx, end_idx)
        """
        detail = []
        sentences=[]
        self.check_corrector_initialized()
        # 长句切分为短句
        # sentences = re.split(r"；|，|。|\?\s|;\s|,\s", sentence)
        maybe_errors = self.detect(sentence)
        # trick: 类似翻译模型，倒序处理
        maybe_errors = sorted(maybe_errors, key=operator.itemgetter(2), reverse=reverse)
        for item, begin_idx, end_idx, err_type in maybe_errors:
            # 纠错，逐个处理
            before_sent = sentence[:begin_idx]
            after_sent = sentence[end_idx:]
            
            # 对非中文的错字不做处理
            if not is_chinese_string(item):
                continue
            # 困惑集中指定的词，直接取结果
            if err_type == ErrorType.confusion:
                corrected_item = self.custom_confusion[item]
            # 对碎片且不常用单字，可能错误是多字少字
            elif err_type == ErrorType.word_char:
                maybe_right_items = self.generate_items_word_char(item, before_sent, after_sent, begin_idx, end_idx)
                corrected_item = self.lm_correct_item(item, maybe_right_items, before_sent, after_sent)
            # 多字
            elif err_type == ErrorType.redundancy:
                maybe_right_items = ['']
                corrected_item = self.lm_correct_item(item, maybe_right_items, before_sent, after_sent)
            else:
                # 取得所有可能正确的词
                maybe_right_items = self.generate_items(item)
                if not maybe_right_items:
                    continue
                corrected_item = self.lm_correct_item(item, maybe_right_items, before_sent, after_sent)
            # output
            if corrected_item != item:
                sentence = before_sent + corrected_item + after_sent
                # logger.debug('predict:' + item + '=>' + corrected_item)
                detail_word = [item, corrected_item, begin_idx, end_idx]
                detail.append(detail_word)
        detail = sorted(detail, key=operator.itemgetter(2))
        return sentence, detail

if __name__ == '__main__':
    # bert_correct = BertCorrector()
    # bert_correct.correct('少先队员因该为老人蝴让座')
    # correct_item = bert_correct.predict_mask_token('少先队员因该为老人蝴让座', 9, 10)
    # print(correct_item)
    c = Corrector()
    # c.enable_word_error(enable=False)
    test2 = '令天突然冷了起来，妈妈丛相子里番出一件旧棉衣让我穿上。我不原意。在妈妈得说服叫育下，我中于穿上哪件棉衣哼着哥儿上学去了。 '
    test1 = '少先队员因该为老让座'
    test3 = '今天在菜园里抓到一只蝴'
    test4 = '在北京京的生活节奏奏是很快的'
    test5='令天突然冷了起来，妈妈丛相子里番出一件旧棉衣让我穿上。我不原意。在妈妈得说服叫育下，我中于穿上哪件棉衣哼着哥儿上学去了。'
    test6 = '我今天了红烧肉'
    test7='这样，你就会尝到泰国人死爱的味道。'
    pred_sentence, pred_detail = c.correct(test7)
    # print(pred_sentence, pred_detail)
    # pred_sentence, pred_detail = c.correct('今天突然冷了起来，妈妈从箱子里翻出一件旧棉衣让我穿上。我不愿意。在妈妈得说服教育下，我终于穿上那件棉衣着哥儿上学去了。')
    # pred_sentence, pred_detail = c.correct(pred_sentence,reverse=False)
    print(pred_sentence, pred_detail)
    c.enable_word_error(enable=True)
    pred_sentence, pred_detail = c.correct(test5)
    print(pred_sentence, pred_detail)