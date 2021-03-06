# -*- coding: utf-8 -*-
'''
@Descripttion: error word detector
@version: 
@Author: cjh <492795090@qq.com>
@Date: 2019-12-19 14:12:17
@LastEditors: cjh <492795090@qq.com>
@LastEditTime: 2020-04-13 10:24:34
'''

import codecs
import time
import sys, os, re
import numpy as np
sys.path.insert(0,os.getcwd())
from mypycorrector import config
from mypycorrector.tokenizer import Tokenizer
from mypycorrector.utils.logger import logger
from mypycorrector.utils.text_utils import uniform, is_alphabet_string

PUNCTUATION_LIST = ".。,，,、?？:：;；{}[]【】“‘’”《》/!！%……（）<>@#$~^￥%&*\"\'=+-_——「」"
# \u4E00-\u9FD5a-zA-Z0-9+#&\._ : All non-space characters. Will be handled with re_han
# \r\n|\s : whitespace characters. Will not be handled.
re_han = re.compile("([\u4E00-\u9FD5a-zA-Z0-9+#&]+)", re.U)
re_skip = re.compile("(\r\n\\s)", re.U)

class ErrorType(object):
    # error_type = {"confusion": 1, "word": 2, "char": 3}
    confusion = 'confusion'
    word = 'word'
    char = 'char'
    redundancy = 'redundancy'   #冗余
    miss = 'miss'  #缺失
    word_char='word_char'   #分词后的碎片单字错误
    


class Detector(object):
    def __init__(self, language_model_path=config.language_model_path,
                 word_freq_path=config.word_freq_path,
                 char_freq_path=config.char_freq_path,
                 custom_word_freq_path=config.custom_word_freq_path,
                 custom_confusion_path=config.custom_confusion_path,
                 person_name_path=config.person_name_path,
                 place_name_path=config.place_name_path,
                 stopwords_path=config.stopwords_path):
        self.name = 'detector'
        self.language_model_path = language_model_path
        self.word_freq_path = word_freq_path
        self.char_freq_path = char_freq_path
        self.custom_word_freq_path = custom_word_freq_path
        self.custom_confusion_path = custom_confusion_path
        self.person_name_path = person_name_path
        self.place_name_path = place_name_path
        self.stopwords_path = stopwords_path
        self.is_char_error_detect = True
        self.is_word_error_detect = True
        self.initialized_detector = False

    def initialize_detector(self):
        t1 = time.time()
        try:
            import kenlm
        except ImportError:
            raise ImportError('mypycorrector dependencies are not fully installed, '
                                'they are required for statistical language model.'
                                'Please use "pip install kenlm" to install it.'
                                'if you are Win, Please install kenlm in cgwin.')

        self.lm = kenlm.Model(self.language_model_path)
        logger.debug('Loaded language model: %s, spend: %s s' %
                        (self.language_model_path, str(time.time() - t1)))

        # 词、频数dict
        t2 = time.time()
        self.word_freq = self.load_word_freq_dict(self.word_freq_path)
        self.char_freq = self.load_char_freq_dict(self.char_freq_path)
        t3 = time.time()
        logger.debug('Loaded word freq, char freq file: %s, size: %d, spend: %s s' %
                     (self.word_freq_path, len(self.word_freq), str(t3 - t2)))
        # 自定义混淆集
        self.custom_confusion = self._get_custom_confusion_dict(
            self.custom_confusion_path)
        t4 = time.time()
        logger.debug('Loaded confusion file: %s, size: %d, spend: %s s' %
                     (self.custom_confusion_path, len(self.custom_confusion), str(t4 - t3)))
        # 自定义切词词典
        self.custom_word_freq = self.load_word_freq_dict(
            self.custom_word_freq_path)
        self.person_names = self.load_word_freq_dict(self.person_name_path)
        self.place_names = self.load_word_freq_dict(self.place_name_path)
        self.stopwords = self.load_word_freq_dict(self.stopwords_path)
        # 合并切词词典及自定义词典
        self.custom_word_freq.update(self.person_names)
        self.custom_word_freq.update(self.place_names)
        self.custom_word_freq.update(self.stopwords)

        self.word_freq.update(self.custom_word_freq)
        t5 = time.time()
        logger.debug('Loaded custom word file: %s, size: %d, spend: %s s' %
                     (self.custom_confusion_path, len(self.custom_word_freq), str(t5 - t4)))
        self.tokenizer = Tokenizer(dict_path=self.word_freq_path, custom_word_freq_dict=self.custom_word_freq,
                                   custom_confusion_dict=self.custom_confusion)
        self.initialized_detector = True

    def check_detector_initialized(self):
        if not self.initialized_detector:
            self.initialize_detector()

    @staticmethod
    def load_word_freq_dict(path):
        """
        加载切词词典
        :param path:
        :return:
        """
        word_freq = {}
        with codecs.open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('#'):
                    continue
                info = line.split()
                if len(info) < 1:
                    continue
                word = info[0]
                # 取词频，默认1
                freq = int(info[1]) if len(info) > 1 else 1
                word_freq[word] = freq
        return word_freq

    @staticmethod
    def load_char_freq_dict(path):
        """
        加载常用字碎片词典
        :param path:
        :return:
        """
        char_freq = {}
        with codecs.open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('#'):
                    continue
                info = line.split()
                if len(info) < 1:
                    continue
                char = info[0]
                # 取词频，默认1
                freq = int(info[1]) if len(info) > 1 else 1
                char_freq[char] = freq
        return char_freq

    def _get_custom_confusion_dict(self, path):
        """
        取自定义困惑集
        :param path:
        :return: dict, {variant: origin}, eg: {"交通先行": "交通限行"}
        """
        confusion = {}
        with codecs.open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('#'):
                    continue
                info = line.split()
                if len(info) < 2:
                    continue
                variant = info[0]
                origin = info[1]
                freq = int(info[2]) if len(info) > 2 else 200
                self.word_freq[origin] = freq
                confusion[variant] = origin
        return confusion

    def set_language_model_path(self, path):
        self.check_detector_initialized()
        import kenlm
        self.lm = kenlm.Model(path)
        logger.debug('Loaded language model: %s' % path)

    def set_custom_confusion_dict(self, path):
        self.check_detector_initialized()
        custom_confusion = self._get_custom_confusion_dict(path)
        self.custom_confusion.update(custom_confusion)
        logger.debug('Loaded confusion path: %s, size: %d' %
                     (path, len(custom_confusion)))

    def set_custom_word(self, path):
        self.check_detector_initialized()
        word_freqs = self.load_word_freq_dict(path)
        # 合并字典
        self.custom_word_freq.update(word_freqs)
        # 合并切词词典及自定义词典
        self.word_freq.update(self.custom_word_freq)
        self.tokenizer = Tokenizer(dict_path=self.word_freq_path, custom_word_freq_dict=self.custom_word_freq,
                                   custom_confusion_dict=self.custom_confusion)
        for k, v in word_freqs.items():
            self.set_word_frequency(k, v)
        logger.debug('Loaded custom word path: %s, size: %d' %
                     (path, len(word_freqs)))

    def enable_char_error(self, enable=True):
        """
        is open char error detect
        :param enable:
        :return:
        """
        self.is_char_error_detect = enable

    def enable_word_error(self, enable=True):
        """
        is open word error detect
        :param enable:
        :return:
        """
        self.is_word_error_detect = enable

    def ngram_score(self, chars):
        """
        取n元文法得分
        :param chars: list, 以词或字切分
        :return:
        """
        self.check_detector_initialized()
        return self.lm.score(' '.join(chars), bos=False, eos=False)

    def ppl_score(self, words):
        """
        取语言模型困惑度得分，越小句子越通顺
        :param words: list, 以词或字切分
        :return:
        """
        self.check_detector_initialized()
        return self.lm.perplexity(' '.join(words))

    def score(self, words):
        """
        Return the log10 probability of a string.
        :param words: list, 以词或字切分
        :return:
        """
        self.check_detector_initialized()
        return self.lm.score(' '.join(words))

    def word_frequency(self, word):
        """
        取词在样本中的词频
        :param word:
        :return:
        """
        self.check_detector_initialized()
        return self.word_freq.get(word, 0)

    def set_word_frequency(self, word, num):
        """
        更新在样本中的词频
        """
        self.check_detector_initialized()
        self.word_freq[word] = num
        return self.word_freq

    @staticmethod
    def _check_contain_error(maybe_err, maybe_errors):
        """
        检测错误集合(maybe_errors)是否已经包含该错误位置（maybe_err)
        :param maybe_err: [error_word, begin_pos, end_pos, error_type]
        :param maybe_errors:
        :return:
        """
        error_word_idx = 0
        begin_idx = 1
        end_idx = 2
        for err in maybe_errors:
            if maybe_err[error_word_idx] in err[error_word_idx] and maybe_err[begin_idx] >= err[begin_idx] and \
                    maybe_err[end_idx] <= err[end_idx]:
                return True
        return False

    def _add_maybe_error_item(self, maybe_err, maybe_errors):
        """
        新增错误
        :param maybe_err:
        :param maybe_errors:
        :return:
        """
        if maybe_err not in maybe_errors and not self._check_contain_error(maybe_err, maybe_errors):
            maybe_errors.append(maybe_err)

    @staticmethod
    def _get_maybe_error_index(scores, ratio=0.6745, threshold=1.4):
        """
        取疑似错字的位置，通过平均绝对离差（MAD）
        :param scores: np.array
        :param threshold: 阈值越小，得到疑似错别字越多
        :return: 全部疑似错误字的index: list
        """
        result = []
        scores = np.array(scores)
        if len(scores.shape) == 1:
            scores = scores[:, None]
        median = np.median(scores, axis=0)  # get median of all scores
        # deviation from the median
        margin_median = np.abs(scores - median).flatten()
        # 平均绝对离差值
        med_abs_deviation = np.median(margin_median)
        if med_abs_deviation == 0:
            return result
        y_score = ratio * margin_median / med_abs_deviation
        # 打平
        scores = scores.flatten()
        maybe_error_indices = np.where(
            (y_score > threshold) & (scores < median))
        # 取全部疑似错误字的index
        result = list(maybe_error_indices[0])
        return result

    @staticmethod
    def is_filter_token(token):
        result = False
        # pass blank
        if not token.strip():
            result = True
        # pass punctuation
        if token in PUNCTUATION_LIST:
            result = True
        # pass num
        if token.isdigit():
            result = True
        # pass alpha
        if is_alphabet_string(token.lower()):
            result = True
        return result

    @staticmethod
    def split_2_short_text(text, include_symbol=False):
        """
        长句切分为短句
        :param text: str
        :param include_symbol: bool
        :return: (sentence, idx)
        """
        result = []
        blocks = re_han.split(text)
        start_idx = 0
        for blk in blocks:
            if not blk:
                continue
            if include_symbol:
                result.append((blk, start_idx))
            else:
                if re_han.match(blk):
                    result.append((blk, start_idx))
            start_idx += len(blk)
        return result
    
    def detect(self, sentence):
        """
        检测句子中的疑似错误信息，包括[词、位置、错误类型]
        :param sentence:
        :return: list[list], [error_word, begin_pos, end_pos, error_type]
        """
        maybe_errors = []
        if not sentence.strip():
            return maybe_errors
        # 初始化
        self.check_detector_initialized()
        # 文本归一化
        sentence = uniform(sentence)
        # 切词
        tokens = self.tokenizer.tokenize(sentence)
        # 自定义混淆集加入疑似错误词典
        # for confuse in self.custom_confusion:
        #     idx = sentence.find(confuse)
        #     if idx > -1:
        #         maybe_err = [confuse, idx, idx +
        #                      len(confuse), ErrorType.confusion]
        #         self._add_maybe_error_item(maybe_err, maybe_errors)

        if self.is_word_error_detect:
            # 未登录词加入疑似错误词典
            for word, begin_idx, end_idx in tokens:
                # pass filter word
                if self.is_filter_token(word):
                    continue
                # pass in dict
                if word in self.word_freq:
                    # # 多字词或词频大于50000的单字，可以continue
                    # if len(word) == 1 and word in self.char_freq and self.char_freq.get(word) < 50000:                                  
                    #     maybe_err = [word, begin_idx, end_idx, ErrorType.word_char]
                    #     self._add_maybe_error_item(maybe_err, maybe_errors)
                    #     continue
                    # # 出现叠字，考虑是否多字
                    # if len(word) == 1 and sentence[begin_idx - 1] == word:
                    #     maybe_err = [word, begin_idx, end_idx, ErrorType.redundancy]
                    #     self._add_maybe_error_item(maybe_err, maybe_errors)
                    continue
                
                # # 对碎片单字进行检测，可能多字、少字、错字
                # if len(word) == 1:
                #     maybe_err = [word, begin_idx, end_idx, ErrorType.word_char]
                #     self._add_maybe_error_item(maybe_err, maybe_errors)
                #     continue
                maybe_err = [word, begin_idx, end_idx, ErrorType.word]
                self._add_maybe_error_item(maybe_err, maybe_errors)

        if self.is_char_error_detect:
            # 语言模型检测疑似错误字
            try:
                ngram_avg_scores = []
                for n in [2, 3]:
                    scores = []
                    for i in range(len(sentence) - n + 1):
                        word = sentence[i:i + n]
                        score = self.ngram_score(list(word))
                        scores.append(score)
                    if not scores:
                        continue
                    # 移动窗口补全得分
                    for _ in range(n - 1):
                        scores.insert(0, scores[0])
                        scores.append(scores[-1])
                    avg_scores = [sum(scores[i:i + n]) / len(scores[i:i + n])
                                    for i in range(len(sentence))]
                    ngram_avg_scores.append(avg_scores)

                # 取拼接后的n-gram平均得分
                sent_scores = list(np.average(
                    np.array(ngram_avg_scores), axis=0))
                # 取疑似错字信息
                for i in self._get_maybe_error_index(sent_scores):
                    token = sentence[i]
                    # pass filter word
                    if self.is_filter_token(token):
                        continue
                    # token, begin_idx, end_idx, error_type
                    maybe_err = [token, i, i + 1, ErrorType.char]
                    self._add_maybe_error_item(maybe_err, maybe_errors)
            except IndexError as ie:
                logger.warn("index error, sentence:" + sentence + str(ie))
            except Exception as e:
                logger.warn("detect error, sentence:" + sentence + str(e))
        return sorted(maybe_errors, key=lambda k: k[1], reverse=False)

if __name__ == '__main__':
    d = Detector()
    error_sentences = ['少先先队员因该为老人让座',
                       '少先队员因该为老人让坐',
                       '少 先 队 员 因 该 为老人让座',
                       '少 先 队 员 因 该 为老人让坐',
                       '机七学习是人工智能领遇最能体现智能的一个分支',
                       '机七学习是人工智能领遇最能体现智能的一个分知']
    t1 = time.time()
    # for sent in error_sentences:
    #     err = d.detect(sent)
    #     print("original sentence:{} => detect sentence:{}".format(sent, err))
    test = '老师工作非常幸苦，我们要遵敬老师。'
    err = d.detect(test)
    print("original sentence:{} => detect sentence:{}".format(test, err))
