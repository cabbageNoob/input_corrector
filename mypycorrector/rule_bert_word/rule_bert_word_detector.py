'''
@Descripttion: 
@version: 
@Author: cjh <492795090@qq.com>
@Date: 2020-01-03 19:04:59
@LastEditors  : cjh <492795090@qq.com>
@LastEditTime : 2020-01-04 11:59:20
'''
import codecs
import time
import sys, os
import numpy as np
sys.path.insert(0, os.getcwd())

import torch
from pytorch_transformers import BertForMaskedLM
from pytorch_transformers import BertTokenizer

from mypycorrector.rule_bert_word import config
from mypycorrector.tokenizer import Tokenizer
from mypycorrector.utils.logger import logger
from mypycorrector.utils.text_utils import uniform, is_alphabet_string

PUNCTUATION_LIST = ".。,，,、?？:：;；{}[]【】“‘’”《》/!！%……（）<>@#$~^￥%&*\"\'=+-_——「」"

class InputFeatures(object):
    """A single set of features of data."""
    def __init__(self, input_ids,
                 segment_ids=None,
                 mask_ids=None,
                 masked_lm_labels=None,
                 input_tokens=None,
                 id=None,
                 token=None):
        self.input_ids = input_ids
        self.segment_ids = segment_ids
        self.mask_ids = mask_ids
        self.masked_lm_labels = masked_lm_labels
        self.input_tokens = input_tokens
        self.id = id
        self.token = token

class ErrorType(object):
    # error_type = {"confusion": 1, "word": 2, "char": 3}
    confusion = 'confusion'
    word = 'word'
    char = 'char'

class RuleBertWordDetector(object):
    def __init__(self, language_model_path=config.language_model_path,
                 word_freq_path=config.word_freq_path,
                 custom_word_freq_path=config.custom_word_freq_path,
                 custom_confusion_path=config.custom_confusion_path,
                 person_name_path=config.person_name_path,
                 place_name_path=config.place_name_path,
                 stopwords_path=config.stopwords_path,
                 bert_model_dir=config.bert_model_dir,
                 bert_model_vocab=config.bert_model_vocab,
                 threshold=0.1):
        self.name = 'rule_bert_word_detector'
        self.language_model_path = language_model_path
        self.word_freq_path = word_freq_path
        self.custom_word_freq_path = custom_word_freq_path
        self.custom_confusion_path = custom_confusion_path
        self.person_name_path = person_name_path
        self.place_name_path = place_name_path
        self.stopwords_path = stopwords_path
        self.is_char_error_detect = True
        self.is_word_error_detect = True
        self.initialized_detector = False
        self.bert_model_dir = bert_model_dir
        self.bert_model_vocab = bert_model_vocab
        self.threshold = threshold
        
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
        t3 = time.time()
        logger.debug('Loaded word freq file: %s, size: %d, spend: %s s' %
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
        # bert预训练模型
        t6 = time.time()
        self.bert_tokenizer = BertTokenizer(vocab_file=self.bert_model_vocab)
        self.MASK_TOKEN = "[MASK]"
        self.MASK_ID = self.bert_tokenizer.convert_tokens_to_ids([self.MASK_TOKEN])[0]
        # Prepare model
        self.model = BertForMaskedLM.from_pretrained(self.bert_model_dir)
        logger.debug("Loaded model ok, path: %s, spend: %.3f s." % (self.bert_model_dir, time.time() - t6))
        self.initialized_detector = True

    def check_detector_initialized(self):
        if not self.initialized_detector:
            self.initialize_detector()

    def _convert_sentence_to_detect_features(self, sentence):
        """Loads a sentence into a list of `InputBatch`s."""
        self.check_detector_initialized()
        features = []
        tokens = self.bert_tokenizer.tokenize(sentence)
        token_ids = self.bert_tokenizer.convert_tokens_to_ids(tokens)
        for idx, token_id in enumerate(token_ids):
            masked_lm_labels = [-1] * len(token_ids)
            masked_lm_labels[idx] = token_id
            features.append(
                InputFeatures(input_ids=token_ids,
                              masked_lm_labels=masked_lm_labels,
                              input_tokens=tokens,
                              id=idx,
                              token=tokens[idx]))
        return features

    # bert 预测可能的错误字    
    def predict_token_prob(self, sentence):
        self.check_detector_initialized()
        result = []
        eval_features = self._convert_sentence_to_detect_features(sentence)

        for f in eval_features:
            input_ids = torch.tensor([f.input_ids])
            masked_lm_labels = torch.tensor([f.masked_lm_labels])
            outputs = self.model(input_ids, masked_lm_labels=masked_lm_labels)
            masked_lm_loss, predictions = outputs[:2]
            prob = np.exp(-masked_lm_loss.item())
            result.append([prob, f])
        return result

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
                freq = int(info[2]) if len(info) > 2 else 1
                self.word_freq[origin] = freq
                confusion[variant] = origin
        return confusion

    def ngram_score(self, chars):
        """
        取n元文法得分
        :param chars: list, 以词或字切分
        :return:
        """
        self.check_detector_initialized()
        return self.lm.score(' '.join(chars), bos = False, eos = False)
        
    def ppl_score(self, words):
        """
        取语言模型困惑度得分，越小句子越通顺
        :param words: list, 以词或字切分
        :return:
        """
        self.check_detector_initialized()
        return self.lm.perplexity(' '.join(words))

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
        # print(tokens)
        # 自定义混淆集加入疑似错误词典
        for confuse in self.custom_confusion:
            idx = sentence.find(confuse)
            if idx > -1:
                maybe_err = [confuse, idx, idx +
                             len(confuse), ErrorType.confusion]
                self._add_maybe_error_item(maybe_err, maybe_errors)

        if self.is_word_error_detect:
            # 未登录词加入疑似错误词典
            for word, begin_idx, end_idx in tokens:
                # pass filter word
                if self.is_filter_token(word):
                    continue
                # pass in dict
                if word in self.word_freq:
                    continue
                maybe_err = [word, begin_idx, end_idx, ErrorType.word]
                self._add_maybe_error_item(maybe_err, maybe_errors)

        if self.is_char_error_detect:
            # 语言模型检测疑似错误字
            try:
                for prob, f in self.predict_token_prob(sentence):
                    # logger.debug('prob:%s, token:%s, idx:%s' % (prob, f.token, f.id))
                    if prob < self.threshold:
                        maybe_err = [f.token, f.id, f.id + 1, ErrorType.char]
                        self._add_maybe_error_item(maybe_err, maybe_errors)
                return maybe_errors
            except IndexError as ie:
                logger.warn("index error, sentence:" + sentence + str(ie))
            except Exception as e:
                logger.warn("detect error, sentence:" + sentence + str(e))
        return sorted(maybe_errors, key=lambda k: k[1], reverse=False)


if __name__ == '__main__':
    d = RuleBertWordDetector()

    error_sentences = ['少先队员因该为老人让座',
                       '少先队员因该为老人让坐',
                       '少 先 队 员 因 该 为老人让座',
                       '少 先 队 员 因 该 为老人让坐',
                       '机七学习是人工智能领遇最能体现智能的一个分支',
                       '机七学习是人工智能领遇最能体现智能的一个分知']
    t1 = time.time()
    for sent in error_sentences:
        err = d.detect(sent)
        print("original sentence:{} => detect sentence:{}".format(sent, err))

       