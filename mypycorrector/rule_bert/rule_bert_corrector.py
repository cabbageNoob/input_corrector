'''
@Descripttion: 
@version: 
@Author: cjh <492795090@qq.com>
@Date: 2019-12-26 22:53:22
@LastEditors  : cjh <492795090@qq.com>
@LastEditTime : 2019-12-28 09:52:34
'''
import operator
import sys, os
import time
import codecs
import numpy as np
sys.path.insert(0,os.getcwd())

import torch

sys.path.insert(0,os.getcwd())
from mypycorrector.rule_bert import config
from mypycorrector.rule_bert.rule_bert_detector import RuleBertDetector, InputFeatures
from mypycorrector.detector import ErrorType
from mypycorrector.utils.text_utils import is_chinese_string
from mypycorrector.utils.logger import logger


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
                same_pron_same_tone = set(list(parts[1]))
                same_pron_diff_tone = set(list(parts[2]))
                value = same_pron_same_tone.union(same_pron_diff_tone)
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
                for i, c in enumerate(parts):
                    result[c] = set(list(parts[:i] + parts[i + 1:]))
    return result
class RuleBertCorrector(RuleBertDetector):
    def __init__(self, bert_model_dir=config.bert_model_dir,
                 bert_model_vocab=config.bert_model_vocab,
                 max_seq_length=config.max_seq_length,
                 threshold=config.threshold,
                 same_pinyin_path=config.same_pinyin_path,
                 same_stroke_path=config.same_stroke_path,):
        super(RuleBertCorrector, self).__init__(bert_model_dir=bert_model_dir,
                                            bert_model_vocab=bert_model_vocab,
                                            threshold=threshold)
        self.name = 'bert_corrector'
        self.bert_model_dir = bert_model_dir
        self.bert_model_vocab = bert_model_vocab
        self.max_seq_length = max_seq_length
        self.initialized_rule_bert_corrector = False
        self.same_pinyin_text_path = same_pinyin_path
        self.same_stroke_text_path = same_stroke_path

    def initialize_rule_bert_corrector(self):
        t1 = time.time()
        # same pinyin
        self.same_pinyin = load_same_pinyin(self.same_pinyin_text_path)
        # same stroke
        self.same_stroke = load_same_stroke(self.same_stroke_text_path)
        logger.debug("Loaded same pinyin file: %s, same stroke file: %s, spend: %.3f s." % (
            self.same_pinyin_text_path, self.same_stroke_text_path, time.time() - t1))
        self.initialized_rule_bert_corrector = True

    def check_rule_bert_corrector_initialized(self):
        if not self.initialized_rule_bert_corrector:
            self.initialize_rule_bert_corrector()
    
    def check_vocab_has_all_token(self, sentence):
        flag = True
        for i in list(sentence):
            if i not in self.bert_tokenizer.vocab:
                flag = False
                break
        return flag
    
    def get_same_pinyin(self, char):
        """
        取同音字
        :param char:
        :return:
        """
        self.check_rule_bert_corrector_initialized()
        return self.same_pinyin.get(char, set())

    def get_same_stroke(self, char):
        """
        取形似字
        :param char:
        :return:
        """
        self.check_rule_bert_corrector_initialized()
        return self.same_stroke.get(char, set())
    
    def _confusion_char_set(self, c):
        return self.get_same_pinyin(c).union(self.get_same_stroke(c))

    def generate_items(self, word, fraction=1):
        """
        生成音近、形近纠错候选集
        :param word:
        :param fraction:
        :return:
        """
        candidates = []
        # same pinyin char
        if len(word) == 1:
            # same one char pinyin
            confusion = [i for i in self._confusion_char_set(word[0]) if i]
            candidates.extend(confusion)
        return candidates
    
    def _convert_sentence_to_correct_features(self, sentence, candidates,begin_idx,end_idx):
        self.check_bert_detector_initialized()
        features = []
        tokens = self.bert_tokenizer.tokenize(sentence)
        token_ids = self.bert_tokenizer.convert_tokens_to_ids(tokens)
        for candidate in candidates:
            candidate_id = self.bert_tokenizer.convert_tokens_to_ids([candidate])[0]
            token_ids_new=token_ids[:]
            token_ids_new[begin_idx] = candidate_id
            tokens_new=tokens[:]
            tokens_new[begin_idx]=candidate
            masked_lm_labels = [-1] * len(token_ids)
            masked_lm_labels[begin_idx] = candidate_id
            features.append(
                InputFeatures(input_ids=token_ids_new,
                              masked_lm_labels=masked_lm_labels,
                              input_tokens=tokens_new,
                              id=begin_idx,
                              token=candidate))
        return features
        
    
    def predict_candidates_prob(self, cur_item,sentence, candidates, begin_idx, end_idx):
        '''
        @Descripttion: 返回candidates中每个prob
        @param {type} 
        @return: 
        '''
        if cur_item not in candidates:
            candidates.append(cur_item)
        self.check_bert_detector_initialized()
        result = []
        eval_features = self._convert_sentence_to_correct_features(sentence, candidates, begin_idx, end_idx)
        for f in eval_features:
            input_ids = torch.tensor([f.input_ids])
            masked_lm_labels = torch.tensor([f.masked_lm_labels])
            outputs = self.model(input_ids, masked_lm_labels=masked_lm_labels)
            masked_lm_loss, predictions = outputs[:2]
            prob = np.exp(-masked_lm_loss.item())
            result.append([prob, f])
        return result
        
    
    def predict_mask_token(self, cur_item, sentence, candidates,begin_idx, end_idx):
        candidates_probs = self.predict_candidates_prob(cur_item, sentence, candidates, begin_idx, end_idx)
        candidates_probs=[[candidate_prob[0],candidate_prob[1].token] for candidate_prob in candidates_probs]
        correct_item = max(candidates_probs)
        return correct_item[1]

    def correct(self, sentence=''):
        """
        句子改错
        :param sentence: 句子文本
        :return: 改正后的句子, list(wrong, right, begin_idx, end_idx)
        """
        detail = []
        maybe_errors = self.detect(sentence)
        for cur_item, begin_idx, end_idx, err_type in maybe_errors:
            # 纠错，逐个处理
            before_sent = sentence[:begin_idx]
            after_sent = sentence[end_idx:]

            if err_type == ErrorType.char:
                # 对非中文的错字不做处理
                if not is_chinese_string(cur_item):
                    continue
                if not self.check_vocab_has_all_token(sentence):
                    continue
                # 取得候选集
                candidates = self.generate_items(cur_item)
                if not candidates:
                    continue
                # 取得最可能正确的字
                corrected_item = self.predict_mask_token(cur_item, sentence, candidates, begin_idx, end_idx)
                
            elif err_type == ErrorType.word:
                corrected_item = cur_item
            else:
                print('not strand error_type')
            # output
            if corrected_item != cur_item:
                sentence = before_sent + corrected_item + after_sent
                detail_word = [cur_item, corrected_item, begin_idx, end_idx]
                detail.append(detail_word)
        detail = sorted(detail, key=operator.itemgetter(2))
        return sentence, detail




if __name__ == '__main__':
    corrector = RuleBertCorrector()
    error_sentences = ['少先队员因该为老人让座',
                       '少先队员因该为老人让坐',
                       '少 先 队 员 因 该 为老人让座',
                       '少 先 队 员 因 该 为老人让坐',
                       '机七学习是人工智能领遇最能体现智能的一个分支',
                       '机七学习是人工智能领遇最能体现智能的一个分知']
    for sentence in error_sentences:
        corrector.correct(sentence)
    # print(d.detect(test))
    