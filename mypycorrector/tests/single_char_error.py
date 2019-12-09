# -*- coding: utf-8 -*-
"""
@author:cjh（492795090@qq.com)
@data:19-11-25
@description: 
"""

# 那天花板上的钻石可比鸡弹（（蛋））还大啊。
# 才般（（搬））进装修好没多久的新宫殿里。
# 做的最倒霉的一件事就帮尼哥檫（（擦））脚。
# 一但（（旦））死去，以前花费的心血都会归零。
# 战士微笑著（（着））轻轻拍了拍少年的肩膀。
# 差点拌（（绊））到自己的脚。
# 面对着熙熙嚷嚷（（攘攘））的城市。
# 你等我和老大商却（（榷））一下。
# 这家伙还蛮格（（恪））尽职守的。
# 玩家取明（（名））“什么”已被占用。
# 报应接中迩（（而））来。
# 人群穿（（川））流不息。
# 这个消息不径（（胫））而走。
# 眼前的场景美仑（（轮））美幻简直超出了人类的想象。
# 看着这两个人谈笑风声（（生））我心理（（里））不由有些忌妒。
# 有老怪坐阵（（镇））难怪他们高枕无忧了。
# 有了这一番旁证（（征））博引。
text = ['那天花板上的钻石可比鸡弹还大啊',
        '才般进装修好没多久的新宫殿里。',
        '做的最倒霉的一件事就帮尼哥檫脚。',
        '一但死去，以前花费的心血都会归零。',
        '战士微笑著轻轻拍了拍少年的肩膀。',
        '差点拌到自己的脚。',
        '面对着熙熙嚷嚷的城市。',
        '你等我和老大商却一下。',
        '这家伙还蛮格尽职守的。',
        '玩家取明“什么”已被占用。',
        '报应接中迩来。',
        '人群穿流不息。',
        '这个消息不径而走。',
        '眼前的场景美仑美幻简直超出了人类的想象。',
        '看着这两个人谈笑风声我心理不由有些忌妒。',
        '有老怪坐阵难怪他们高枕无忧了。',
        '有了这一番旁证博引。',
        ]

import sys

sys.path.append('..')
import pycorrector


def test1():
    for i in text:
        print(i, pycorrector.detect(i))
        print(i, pycorrector.correct(i))


x = ['这家伙还蛮格尽职守的',
     '做的最倒霉的一件事就帮尼哥檫脚',
     '那天花板上的钻石可比鸡弹还大啊',
     '有老怪坐阵难怪他们高枕无忧了',
     '战士微笑著轻轻拍了拍少年的肩膀',
     '差点拌到自己的脚',
     '你等我和老大商却一下',

     '报应接中迩来',
     '这个消息不径而走',
     '眼前的场景美仑美幻简直超出了人类的想象',
     '看着这两个人谈笑风声我心理不由有些忌妒',
     '有了这一番旁证博引']


def test2():
    for i in x:
        print(i, pycorrector.detect(i))
        print(i, pycorrector.correct(i))


if __name__ == '__main__':
    test1()
    test2()
