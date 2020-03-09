'''
@Descripttion: 
@version: 
@Author: cjh <492795090@qq.com>
@Date: 2020-01-04 12:02:32
@LastEditors: cjh <492795090@qq.com>
@LastEditTime: 2020-03-09 20:32:57
'''
import codecs
import operator
import os, sys
import time
from math import pow
import torch
sys.path.insert(0, os.getcwd())

from pypinyin import lazy_pinyin
from mypycorrector.rule_bert_word import config
from mypycorrector.rule_bert_word.rule_bert_word_detector import RuleBertWordDetector, ErrorType, InputFeatures
from mypycorrector.utils.logger import logger
from mypycorrector.utils.math_utils import edit_distance_word
from mypycorrector.utils.text_utils import is_chinese_string
from mypycorrector.utils.logger import logger

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

class RuleBertWordCorrector(RuleBertWordDetector):
    def __init__(self, common_char_path=config.common_char_path,
                 same_pinyin_path=config.same_pinyin_path,
                 same_stroke_path=config.same_stroke_path,
                 language_model_path=config.language_model_path,
                 word_freq_path=config.word_freq_path,
                 custom_word_freq_path=config.custom_word_freq_path,
                 custom_confusion_path=config.custom_confusion_path,
                 person_name_path=config.person_name_path,
                 place_name_path=config.place_name_path,
                 stopwords_path=config.stopwords_path,
                 bert_model_dir=config.bert_model_dir,
                 bert_model_vocab=config.bert_model_vocab,
                 max_seq_length=config.max_seq_length,
                 threshold=config.threshold):
        super(RuleBertWordCorrector, self).__init__(language_model_path=language_model_path,
                                        word_freq_path=word_freq_path,
                                        custom_word_freq_path=custom_word_freq_path,
                                        custom_confusion_path=custom_confusion_path,
                                        person_name_path=person_name_path,
                                        place_name_path=place_name_path,
                                        stopwords_path=stopwords_path,
                                        bert_model_dir=bert_model_dir,
                                        bert_model_vocab=bert_model_vocab,
                                        threshold=threshold)
        self.name = 'rule_bert_word_corrector'
        self.max_seq_length = max_seq_length
        self.common_char_path = common_char_path
        self.same_pinyin_text_path = same_pinyin_path
        self.same_stroke_text_path = same_stroke_path
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
        self.initialized_corrector = True

    def check_corrector_initialized(self):
        if not self.initialized_corrector:
            self.initialize_corrector()

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
        # confusion_sorted=[(item,ErrorType.word) for item in confusion_sorted]
        return confusion_sorted[:len(confusion_word_list) // fraction + 1]

    def generate_items_for_word(self, word, fraction=1):
        candidates_2_order = []
        candidates_3_order = []
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
        confusion_word_set = set(candidates_2_order + candidates_3_order)
        confusion_word_list = [item for item in confusion_word_set if is_chinese_string(item)]
        confusion_sorted = sorted(confusion_word_list, key=lambda k: self.word_frequency(k), reverse=True)
        return confusion_sorted[:len(confusion_word_list) // fraction + 1]

    def generate_items_word_char(self, char, before_sent, after_sent, begin_idx, end_idx):
        '''
        @Descripttion: 生成可能多字少字误字的候选集
        @param {type} 
        @return: 
        '''   
        candidates = []
        # same one char pinyin
        confusion = [(i,ErrorType.word) for i in self._confusion_char_set(char) if i]
        candidates.extend(confusion)
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
        if item not in [maybe_right_item[0] for maybe_right_item in maybe_right_items]:
            maybe_right_items.append((item,'itself'))
        corrected_item = min(maybe_right_items, key=lambda k: self.ppl_score(list(before_sent + k[0] + after_sent)))
        # corrected_items=heapq.nsmallest(5,maybe_right_items,key=lambda k: self.ppl_score(list(before_sent + k + after_sent)))
        return corrected_item

    def _convert_sentence_to_correct_features(self, sentence, begin_idx, end_idx):
        """Loads a sentence into a list of `InputBatch`s."""
        features = []
        tokens_a = self.bert_tokenizer.tokenize(sentence)

        # For single sequences:
        #  tokens:   [CLS] the dog is hairy . [SEP]
        #  type_ids: 0      0   0   0  0    0   0
        tokens = ["[CLS]"] + tokens_a + ["[SEP]"]
        k = begin_idx + 1
        for i in range(end_idx - begin_idx):
            tokens[k] = '[MASK]'
            k += 1
        segment_ids = [0] * len(tokens)

        input_ids = self.bert_tokenizer.convert_tokens_to_ids(tokens)
        mask_ids = [i for i, v in enumerate(input_ids) if v == self.MASK_ID]

        # Zero-pad up to the sequence length.
        padding = [0] * (self.max_seq_length - len(input_ids))
        input_ids += padding
        segment_ids += padding

        features.append(
            InputFeatures(input_ids=input_ids,
                            mask_ids=mask_ids,
                            segment_ids=segment_ids,
                            input_tokens=tokens))

        return features

    def predict_mask_token_(self, sentence, error_begin_idx, error_end_idx):
        # 用于缺字，完形填空
        corrected_item = sentence[error_begin_idx:error_end_idx]
        eval_features = self._convert_sentence_to_correct_features(
            sentence=sentence,
            begin_idx=error_begin_idx,
            end_idx=error_end_idx
        )

        for f in eval_features:
            input_ids = torch.tensor([f.input_ids])
            segment_ids = torch.tensor([f.segment_ids])
            outputs = self.model(input_ids, segment_ids)
            predictions = outputs[0]
            # confirm we were able to predict 'henson'
            masked_ids = f.mask_ids
            if masked_ids:
                for idx, i in enumerate(masked_ids):
                    predicted_index = torch.argmax(predictions[0, i]).item()
                    # predicted_indexes = torch.topk(predictions[0, i], 10)
                    # predicted_indexes=list(predicted_indexes.indices.numpy())
                    # print(predicted_indexes)
                    predicted_token = self.bert_tokenizer.convert_ids_to_tokens([predicted_index])[0]
                    # logger.debug('original text is: %s' % f.input_tokens)
                    # logger.debug('Mask predict is: %s' % predicted_token)
                    corrected_item = predicted_token
        return corrected_item

    def predict_mask_token(self, cur_item, sentence, candidates, begin_idx, end_idx):
        if cur_item not in candidates:
            candidates.append(cur_item)
        eval_features = self._convert_sentence_to_correct_features(
            sentence=sentence,
            begin_idx=begin_idx,
            end_idx=end_idx
        )
        
        for f in eval_features:
            input_ids = torch.tensor([f.input_ids])
            segment_ids = torch.tensor([f.segment_ids])
            outputs = self.model(input_ids, segment_ids)
            predictions = outputs[0]
            # confirm we were able to predict 'henson'
            masked_ids = f.mask_ids
            if masked_ids:
                for idx, i in enumerate(masked_ids):
                    candidates_ids = self.bert_tokenizer.convert_tokens_to_ids(candidates)
                    candidates_probs = [[float(predictions[0, i, candidate_id].data), candidate] for candidate_id,candidate in zip(candidates_ids,candidates)]
                    # predicted_index = torch.argmax(predictions[0, i]).item()
                    # predicted_indexes = torch.topk(predictions[0, i], 10)
                    # predicted_indexes=list(predicted_indexes.indices.numpy())
                    # print(predicted_indexes)
                    # predicted_token = self.bert_tokenizer.convert_ids_to_tokens([predicted_index])[0]
                    predicted_token=max(candidates_probs)[1]
                    # logger.debug('original text is: %s' % f.input_tokens)
                    # logger.debug('Mask predict is: %s' % predicted_token)
                    corrected_item = predicted_token
        return corrected_item
    
    def correct(self, sentence,reverse=True):
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
        maybe_errors = sorted(maybe_errors, key=operator.itemgetter(2), reverse=True)
        for cur_item, begin_idx, end_idx, err_type in maybe_errors:
            # 纠错，逐个处理
            before_sent = sentence[:begin_idx]
            after_sent = sentence[end_idx:]
            # 对非中文的错字不做处理
            if not is_chinese_string(cur_item):
                continue
            # 困惑集中指定的词，直接取结果
            if err_type == ErrorType.confusion:
                # corrected_item = self.custom_confusion[item]
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
                if corrected_item[0] not in self.word_freq:
                    candidates = self.generate_items_for_word(corrected_item[0])
                    if not candidates:
                        continue
                    candidates=[(item,ErrorType.word) for item in candidates]
                    corrected_item = self.lm_correct_item(cur_item, candidates, before_sent, after_sent)
            else:
                '''err_type == ErrorType.char'''
                # 取得所有可能正确的词
                candidates = self.generate_items(cur_item)
                if not candidates:
                    continue
                # 取得最可能正确的字
                corrected_item = self.predict_mask_token(cur_item, sentence, candidates, begin_idx, end_idx)
                corrected_item = (corrected_item, ErrorType.char)
            # output
            if corrected_item[0] != cur_item:
                sentence = before_sent + corrected_item[0] + after_sent
                detail_word = [cur_item, corrected_item[0], begin_idx, end_idx,corrected_item[1]]
                detail.append(detail_word)

        detail = sorted(detail, key=operator.itemgetter(2))
        return sentence, detail, '/'.join(self.tokens), maybe_errors

if __name__ == '__main__':
    corrector = RuleBertWordCorrector()
    error_sentences = ['少先队员因该为老人让座',
                       '少先队员因该为老人让坐',
                       '少 先 队 员 因 该 为老人让座',
                       '少 先 队 员 因 该 为老人让坐',
                       '机七学习是人工智能领遇最能体现智能的一个分支',
                       '机七学习是人工智能领遇最能体现智能的一个分知']
    # corrector.enable_word_error(enable=False)
    test='令天突然冷了起来，妈妈丛相子里番出一件旧棉衣让我穿上。我不原意。在妈妈得说服叫育下，我中于穿上哪件棉衣哼着哥儿上学去了。'
    pred_sentence, pred_detail,tokens,maybe_errors = corrector.correct(test)
    print(pred_sentence, pred_detail,tokens)
    corrector.enable_word_error(enable=True)
    pred_sentence, pred_detail,tokens,maybe_errors = corrector.correct(test)
    print(pred_sentence, pred_detail,tokens)
    # for sentence in error_sentences:
    #     pred_sentence, pred_detail = corrector.correct(sentence)
    #     print("origin_sentence:",sentence)
    #     print("pred_sentence:", pred_sentence)
    #     print("pred_detail:",pred_detail)
    