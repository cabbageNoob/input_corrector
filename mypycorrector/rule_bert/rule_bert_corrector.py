'''
@Descripttion: 
@version: 
@Author: cjh <492795090@qq.com>
@Date: 2019-12-26 22:53:22
@LastEditors  : cjh <492795090@qq.com>
@LastEditTime : 2019-12-26 23:00:01
'''
import sys, os
sys.path.insert(0,os.getcwd())
from mypycorrector.rule_bert.rule_bert_detector import RuleDetector

if __name__ == '__main__':
    d = RuleDetector()
    test = '佳如爱有天意'
    print(d.detect(test))
    