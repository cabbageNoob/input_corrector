'''
@Descripttion: 
@version: 
@Author: cjh <492795090@qq.com>
@Date: 2020-01-03 19:03:59
@LastEditors: cjh <492795090@qq.com>
@LastEditTime: 2020-03-09 11:25:51
'''
import os

pwd_path = os.path.abspath(os.path.dirname(__file__))

bert_model_dir = os.path.join(pwd_path, '../data/bert_models/chinese_finetuned_lm')
bert_model_vocab = os.path.join(pwd_path, '../data/bert_models/chinese_finetuned_lm/vocab.txt')
output_dir = os.path.join(pwd_path, './output')
max_seq_length = 128
threshold = 0.1

# 通用分词词典文件  format: 词语 词频
word_freq_path = os.path.join(pwd_path, '../data/word_freq.txt')
# 通用常用单字字典文件 format:字，字频
char_freq_path = os.path.join(pwd_path, '../data/char_freq.txt')
# 中文常用字符集
common_char_path = os.path.join(pwd_path, '../data/common_char_set.txt')
# 同音字
same_pinyin_path = os.path.join(pwd_path, '../data/same_pinyin.txt')
# 形似字
same_stroke_path = os.path.join(pwd_path, '../data/same_stroke.txt')
# language model path
language_model_path = os.path.join(pwd_path, '../data/kenlm/people2014corpus_chars.klm')#people2014corpus_chars.klm  #THUCNews_char.klm  #THUCNews_people2014_merge_char.klm
# 用户自定义错别字混淆集  format:变体	本体   本体词词频（可省略）
custom_confusion_path = os.path.join(pwd_path, '../data/custom_confusion.txt')
# 用户自定义分词词典  format: 词语 词频
custom_word_freq_path = os.path.join(pwd_path, '../data/custom_word_freq.txt')
# 知名人名词典 format: 词语 词频
person_name_path = os.path.join(pwd_path, '../data/person_name.txt')
# 地名词典 format: 词语 词频
place_name_path = os.path.join(pwd_path, '../data/place_name.txt')
# 停用词
stopwords_path = os.path.join(pwd_path, '../data/stopwords.txt')
