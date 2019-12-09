# -*- coding: utf-8 -*-
# Author: cjh（492795090@qq.com）
# Brief: mypycorrector.api

from .corrector import Corrector
from .detector import Detector
from .utils.logger import set_log_level
from .utils.text_utils import get_homophones_by_char, get_homophones_by_pinyin
from .utils.text_utils import traditional2simplified, simplified2traditional

__version__ = '0.1.9'

corrector = Corrector()
get_same_pinyin = corrector.get_same_pinyin
get_same_stroke = corrector.get_same_stroke
set_custom_confusion_dict = corrector.set_custom_confusion_dict
set_custom_word = corrector.set_custom_word
set_language_model_path = corrector.set_language_model_path
correct = corrector.correct
ngram_score = corrector.ngram_score
ppl_score = corrector.ppl_score
lm_correct_sentece = corrector.lm_correct_sentece
word_frequency = corrector.word_frequency
detect = corrector.detect
enable_char_error = corrector.enable_char_error
enable_word_error = corrector.enable_word_error
set_log_level = set_log_level

score = corrector.score
