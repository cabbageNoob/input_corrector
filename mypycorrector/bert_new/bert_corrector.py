'''
@Descripttion: use bert detect and correct chinese char error
@version: 
@Author: cjh (492795090@qq.com)
@Date: 2020-03-18 07:33:36
@LastEditors: cjh <492795090@qq.com>
@LastEditTime: 2020-04-30 21:23:07
'''
# -*- coding: utf-8 -*-
import operator
import sys,os
import time
import torch

from transformers import pipeline
pwd_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append('../..')
sys.path.insert(0,os.getcwd())
from mypycorrector.bert_new import config
from mypycorrector.utils.text_utils import is_chinese_string, convert_to_unicode
from mypycorrector.utils.text_utils import uniform, is_alphabet_string
from mypycorrector.utils.logger import logger
from mypycorrector.utils.ssc_utils import computeSSCSimilarity,computeSoundCodeSimilarity,computeShapeCodeSimilarity
from mypycorrector.utils.knn_utils import KNearestNeighbor
from mypycorrector.utils.neural_network_utils import Net
from mypycorrector.utils import neural_network_utils
from mypycorrector.corrector import Corrector
from mypycorrector.detector import ErrorType



class BertCorrector(Corrector):
    def __init__(self, bert_model_dir=config.bert_model_dir,
                 bert_config_path=config.bert_config_path,
                 bert_model_path=config.bert_model_path,
                 hanzi_ssc_path=config.hanzi_ssc_path):
                #  bert_config_path='../data/bert_models/chinese_finetuned_lm/config.json',
                #  bert_model_path='../data/bert_models/chinese_finetuned_lm/pytorch_model.bin'):
        super(BertCorrector, self).__init__()
        self.name = 'bert_corrector'
        t1 = time.time()
        self.hanziSSCDict = self._getHanziSSCDict(hanzi_ssc_path)
        logger.debug('Loaded ssc dict: %s, spend: %.3f s.' % (hanzi_ssc_path, time.time() - t1))
        t1 = time.time()
        self.model = pipeline('fill-mask',
                              model=bert_model_path,
                              config=bert_config_path,
                              tokenizer=bert_model_dir)
        if self.model:
            self.mask = self.model.tokenizer.mask_token
            logger.debug('Loaded bert model: %s, spend: %.3f s.' % (bert_model_dir, time.time() - t1))
        # self.score_data_file=open(config.score_2013_data_new_path,'w',encoding='utf8')
        t1 = time.time()
        self.knn = KNearestNeighbor()
        self.knnTrainingset = self.knn.loadDataset(filename=config.score_2013_data_path, split=0.75)
        logger.debug('Loaded knn training data: %s, spend: %.3f s.' % (config.score_2013_data_path, time.time() - t1))

        t1 = time.time()
        self.neural_model=neural_network_utils.load_model(config.neural_network_model_path)
        logger.debug('Loaded neural network: %s, spend: %.3f s.' % (config.neural_network_model_path, time.time() - t1))

    def _getHanziSSCDict(self, hanzi_ssc_path):
        hanziSSCDict = {}#汉子：SSC码
        with open(hanzi_ssc_path, 'r', encoding='UTF-8') as f:#文件特征：U+4EFF\t仿\t音形码\n
            for line in f:
                line = line.split()
                hanziSSCDict[line[1]] = line[2]
        return hanziSSCDict

    def _getSSC(self, char, encode_way='ALL'):
        ssc = self.hanziSSCDict.get(char, '0' * 11)
        if encode_way=="SOUND":
            ssc=ssc[:4]
        elif encode_way=="SHAPE":
            ssc=ssc[4:]
        else:
            pass
        return ssc

    def ssc_correct_item(self, char, top_tokens):
        '''
        @Descripttion: 通过ssc量化计算字符间相似度，选出最佳tokens
        @param {type} 
        @return: 
        '''
        top_tokens_score = {}
        for token in top_tokens:
            token_str = token.get('token_str')
            bert_score = token.get('bert_score')
            ssc_similar = token.get('ssc_similar')
            if bert_score > 0.1 and ssc_similar > 0.45:
                return token_str
        return char
        # return max(top_tokens_score, key=lambda  k: top_tokens_score[k])
        # return max(top_tokens, key=lambda k: top_tokens[k]*computeSSCSimilarity(char_ssc,self._getSSC(k)))

    def knn_ssc_correct_item(self, char, top_tokens):
        '''
        @Descripttion: knn分类用于过滤，选出最佳tokens
        @param {type} 
        @return: 
        '''
        top_tokens_score = {}
        for token in top_tokens:
            token_str = token.get('token_str')
            bert_score = token.get('bert_score')
            sound_similar = token.get('sound_similar')
            shape_similar = token.get('shape_similar')
            ssc_similar = token.get('ssc_similar')
            if self.knn.getKnnResult(self.knnTrainingset, [bert_score, sound_similar, shape_similar]) == 1:
                return token_str
        return char

    def neural_ssc_correct_item(self, char, top_tokens):
        '''
        @Descripttion: 三层简单神经网络分类器用于过滤，选出最佳tokens
        @param {type} 
        @return: 
        '''
        top_tokens_score = {}
        for token in top_tokens:
            token_str = token.get('token_str')
            bert_score = token.get('bert_score')
            sound_similar = token.get('sound_similar')
            shape_similar = token.get('shape_similar')
            ssc_similar = token.get('ssc_similar')
            if self.neural_model.predict(torch.Tensor([[bert_score, sound_similar, shape_similar]]).type(torch.FloatTensor)) == 1:
                return token_str
        return char
        
    def write2scorefile(self, char, top_tokens, idx, id_lists, right_item):
        if idx not in id_lists:
            return
        for token in top_tokens:
            token_str = token.get('token_str')
            bert_score = token.get('bert_score')
            sound_similar = token.get('sound_similar')
            shape_similar = token.get('shape_similar')
            ssc_similar = token.get('ssc_similar')
            if token_str == right_item:
                self.score_data_file.write(char+','+token_str+','+str(bert_score) + ',' + str(sound_similar) + ',' + \
                str(shape_similar) + ',' + '1' + '\n')
            else:
                self.score_data_file.write(char+','+token_str+','+str(bert_score) + ',' + str(sound_similar) + ',' + \
                str(shape_similar) + ',' + '0' + '\n')
        

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
        # # same pinyin word
        # candidates_1_order.extend(self._confusion_word_set(char))
        # # custom confusion word
        # candidates_1_order.extend(self._confusion_custom_set(char))
        # candidates.extend(candidates_1_order)
        # # same one char pinyin
        # confusion = self._confusion_char_set(char)
        # candidates.extend(confusion)
        # candidates = [(i, ErrorType.word) for i in candidates]
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
                maybe_err = [confuse, idx, idx + len(confuse), ErrorType.confusion]
                self._add_maybe_error_item(maybe_err, maybe_errors)
        
        if self.is_word_error_detect:
            # 未登录词加入疑似错误词典
            for word, begin_idx, end_idx in tokens:
                # pass filter word
                if self.is_filter_token(word):
                    continue
                # pass in dict
                if word in self.word_freq:
                    # 多字词或词频大于50000的单字，可以continue
                    if len(word) == 1 and word in self.char_freq and self.char_freq.get(word) < 10000:                                  
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
                # maybe_err = [word, begin_idx, end_idx, ErrorType.word]
                # self._add_maybe_error_item(maybe_err, maybe_errors)
        return sorted(maybe_errors, key=lambda k: k[1], reverse=False)
    
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
        if self.is_word_error_detect:
            maybe_errors = self.detect(text)
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

        if self.is_char_error_detect:
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

    def correct_short(self, text, start_idx=0):
        text_new = ''
        details = []
        self.check_corrector_initialized()
        # 编码统一，utf-8 to unicode
        text = convert_to_unicode(text)
        if self.is_word_error_detect:
            maybe_errors = self.detect(text)
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
                
                # output
                if corrected_item[0] != cur_item:
                    text = before_sent + corrected_item[0] + after_sent
                    detail_word = [cur_item, corrected_item[0], start_idx+begin_idx, start_idx+end_idx, corrected_item[1]]
                    details.append(detail_word)    

        if self.is_char_error_detect:
            for idx, s in enumerate(text):
                # 对非中文的错误不做处理
                if is_chinese_string(s):
                    sentence_lst = list(text_new + text[idx:])
                    sentence_lst[idx] = self.mask
                    sentence_new = ''.join(sentence_lst)
                    predicts = self.model(sentence_new)
                    top_tokens = []
                    ssc_s = self._getSSC(s)
                    for p in predicts:
                        token_id = p.get('token', 0)
                        token_score = p.get('score', 0)
                        token_str = self.model.tokenizer.convert_ids_to_tokens(token_id)
                        ssc_token = self._getSSC(token_str)
                        soundSimi=computeSoundCodeSimilarity(ssc_s[:4], ssc_token[:4])
                        shapeSimi=computeShapeCodeSimilarity(ssc_s[4:], ssc_token[4:])
                        ssc_similarity = computeSSCSimilarity(ssc_s, ssc_token)
                        top_tokens.append({'bert_score': token_score, 'token_str': token_str, \
                            'ssc_similar': ssc_similarity, 'sound_similar': soundSimi, 'shape_similar': shapeSimi})
                    
                    if top_tokens and (s not in [token.get('token_str') for token in top_tokens]):
                        # correct_item = self.ssc_correct_item(s, top_tokens)
                        correct_item = self.neural_ssc_correct_item(s, top_tokens)
                        if correct_item != s:
                            # details.append([s, correct_item, idx + start_idx, idx + start_idx + 1, ErrorType.char])
                            details.append([s, correct_item, idx + start_idx -1, idx + start_idx, ErrorType.char])
                            s = correct_item
                text_new += s
        details = sorted(details, key=operator.itemgetter(2))
        return text_new[1:], details  

    def bert_correct_ssc_origin(self, text):
        """
        使用ssc音形码进行句子纠错
        :param text: 句子文本
        :return: list[list], [error_word, begin_pos, end_pos, error_type]
        """
        text_new = ''
        details = []
        self.check_corrector_initialized()
        # 编码统一，utf-8 to unicode
        text = convert_to_unicode(text)
        if self.is_char_error_detect:
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
                        ssc_s = self._getSSC(s)
                        for p in predicts:
                            token_id = p.get('token', 0)
                            token_score = p.get('score', 0)
                            token_str = self.model.tokenizer.convert_ids_to_tokens(token_id)
                            ssc_token = self._getSSC(token_str)
                            soundSimi=computeSoundCodeSimilarity(ssc_s[:4], ssc_token[:4])
                            shapeSimi=computeShapeCodeSimilarity(ssc_s[4:], ssc_token[4:])
                            ssc_similarity = computeSSCSimilarity(ssc_s, ssc_token)
                            top_tokens.append({'bert_score': token_score, 'token_str': token_str, \
                                'ssc_similar': ssc_similarity, 'sound_similar': soundSimi, 'shape_similar': shapeSimi})

                        if top_tokens and (s not in [token.get('token_str') for token in top_tokens]):
                            # correct_item = self.ssc_correct_item(s, top_tokens)
                            correct_item = self.neural_ssc_correct_item(s, top_tokens)
                            if correct_item != s:
                                details.append([s, correct_item, idx, idx + 1, ErrorType.char])
                            s = correct_item
                            # 取得所有可能正确的词
                            # candidates = self.generate_items(s)
                            # if candidates:
                            #     for token_str in top_tokens:
                            #         if token_str in candidates:
                            #             details.append([s, token_str, idx, idx + 1,ErrorType.char])
                            #             s = token_str
                            #             break
                text_new += s

        details = sorted(details, key=operator.itemgetter(2))
        return text_new, details

    def bert_correct_ssc(self, text):
        """
        使用ssc音形码进行句子纠错
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
        # blocks = self.split_2_short_text(text)
        if self.is_word_error_detect:
            pass
        
        if self.is_char_error_detect:
            for blk, start_idx in blocks:
                blk_new = ''
                for idx, s in enumerate(blk):
                    # 对非中文的错误不做处理
                    if is_chinese_string(s):
                        sentence_lst = list(blk_new + blk[idx:])
                        sentence_lst[idx] = self.mask
                        sentence_new = ''.join(sentence_lst)
                        predicts = self.model(sentence_new)
                        top_tokens = []
                        ssc_s = self._getSSC(s)
                        for p in predicts:
                            token_id = p.get('token', 0)
                            token_score = p.get('score', 0)
                            token_str = self.model.tokenizer.convert_ids_to_tokens(token_id)
                            ssc_token = self._getSSC(token_str)
                            soundSimi=computeSoundCodeSimilarity(ssc_s[:4], ssc_token[:4])
                            shapeSimi=computeShapeCodeSimilarity(ssc_s[4:], ssc_token[4:])
                            ssc_similarity = computeSSCSimilarity(ssc_s, ssc_token)
                            top_tokens.append({'bert_score': token_score, 'token_str': token_str, \
                                'ssc_similar': ssc_similarity, 'sound_similar': soundSimi, 'shape_similar': shapeSimi})
                       
                        if top_tokens and (s not in [token.get('token_str') for token in top_tokens]):
                            # correct_item = self.ssc_correct_item(s, top_tokens)
                            correct_item = self.neural_ssc_correct_item(s, top_tokens)
                            if correct_item != s:
                                details.append([s, correct_item, idx + start_idx, idx + start_idx + 1, ErrorType.char])
                                s = correct_item
                    blk_new += s
                text_new += blk_new

        details = sorted(details, key=operator.itemgetter(2))
        return text_new, details        

    def generate_bertScore_sound_shape_file(self, text, right_sentence='',id_lists=[]):
        """
        生成bert_score、sound_score、shape_score文件
        :param text: 句子文本
        :return: file
        """
        text_new = ''
        details = []
        self.check_corrector_initialized()
        # 编码统一，utf-8 to unicode
        text = convert_to_unicode(text)
        # 长句切分为短句
        blocks = self.split_2_short_text(text, include_symbol=True)
        if self.is_char_error_detect:
            for blk, start_idx in blocks:
                blk_new = ''
                for idx, s in enumerate(blk):
                    # 对非中文的错误不做处理
                    if is_chinese_string(s):
                        # 对已包含错误不处理
                        maybe_err = [s, idx, idx + 1, ErrorType.char]
                        if not self._check_contain_details_error(maybe_err, details):
                            sentence_lst = list(blk_new + blk[idx:])
                            sentence_lst[idx] = self.mask
                            sentence_new = ''.join(sentence_lst)
                            predicts = self.model(sentence_new)
                            top_tokens = []
                            ssc_s = self._getSSC(s)
                            for p in predicts:
                                token_id = p.get('token', 0)
                                token_score = p.get('score', 0)
                                token_str = self.model.tokenizer.convert_ids_to_tokens(token_id)
                                ssc_token = self._getSSC(token_str)
                                soundSimi=computeSoundCodeSimilarity(ssc_s[:4], ssc_token[:4])
                                shapeSimi=computeShapeCodeSimilarity(ssc_s[4:], ssc_token[4:])
                                ssc_similarity = computeSSCSimilarity(ssc_s, ssc_token)
                                top_tokens.append({'bert_score': token_score, 'token_str': token_str, \
                                    'ssc_similar': ssc_similarity, 'sound_similar': soundSimi, 'shape_similar': shapeSimi})
                        
                            if top_tokens and (s not in [token.get('token_str') for token in top_tokens]):
                                self.write2scorefile(s, top_tokens, start_idx + idx, id_lists, right_sentence[start_idx + idx])
                                # correct_item = self.ssc_correct_item(s, top_tokens)
                                correct_item = right_sentence[start_idx + idx]
                                if correct_item != s:
                                    details.append([s, correct_item, idx + start_idx, idx + start_idx + 1, ErrorType.char])
                                    s = correct_item
                    blk_new += s
                text_new += blk_new
        details = sorted(details, key=operator.itemgetter(2))
        return text_new, details


if __name__ == "__main__":
    d = BertCorrector()
    d.enable_word_error(enable=False)
    error_sentences = [
        '张爱文和林美美不能一起去那理',
        '今天我在菜园里抓到一只蝴',
        '少先队员因该为老人让坐',
        '少 先  队 员 因 该 为 老人让坐',
        '机七学习是人工智能领遇最能体现智能的一个分知',
        '今天心情很好',
    ]
    # for sent in error_sentences:
    #     corrected_sent, err = d.bert_correct_ssc(sent)
    #     print("original sentence:{} => {}, err:{}".format(sent, corrected_sent, err))
    test = '造这堵围墙，是考虑小区的安全，谁知事与愿违，却防碍了救护车的通行。'
    test='今天突然冷了七来，妈妈丛相子里番出一件旧棉衣让我穿上。我不原意。在妈妈得说服叫育下，我中于穿上哪件棉衣哼着哥儿上学去了。'
    test='遇到逆竟时'
    corrected_sent, err = d.generate_bertScore_sound_shape_file(test,right_sentence='遇到逆境时',id_lists=[3])
    print("original sentence:{} => {}, err:{}".format(test, corrected_sent, err))
