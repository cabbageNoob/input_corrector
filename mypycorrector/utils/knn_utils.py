'''
@Descripttion: 
@version: 
@Author: cjh <492795090@qq.com>
@Date: 2020-04-09 09:13:13
@LastEditors: cjh <492795090@qq.com>
@LastEditTime: 2020-04-09 09:36:27
'''
# -*- coding: UTF-8 -*-
import math
import csv
import random
import operator
import sys, os
sys.path.insert(0, os.getcwd())
pwd_path = os.path.abspath(os.path.dirname(__file__))
test_data=os.path.join(pwd_path,'./data/sighan_2013_score_data/score_data_sighan_2013.txt')

class KNearestNeighbor(object):
    def __init__(self):
        pass

    def loadDataset(self, filename, split):  # 加载数据集  split以某个值为界限分类train和test
        trainingSet = []
        testSet = []
        with open(filename, 'r',encoding='utf8') as csvfile:
            lines = csv.reader(csvfile)   #读取所有的行
            dataset = list(lines)  #转化成列表
            data = list()
            for x in range(len(dataset) - 1):
                temp = list()
                for y in range(3):
                    temp.append(float(dataset[x][y + 2]))
                temp.append(int(dataset[x][-1]))
                if random.random() < split:   # 将所有数据加载到train和test中
                    trainingSet.append(temp)
                else:
                    testSet.append(temp)
        return trainingSet


    def calculateDistance(self,testdata, traindata, length):   # 计算距离
        distance = 0     # length表示维度 数据共有几维
        for x in range(length):
            distance += pow((testdata[x]-traindata[x]), 2)
        return math.sqrt(distance)


    def getNeighbors(self,trainingSet, testInstance, k,type_length):  # 返回最近的k个边距
        distances = []
        for x in range(len(trainingSet)):   #对训练集的每一个数计算其到测试集的实际距离
            dist = self.calculateDistance(testInstance, trainingSet[x], type_length)
            # print('训练集:{}-距离:{}'.format(trainingSet[x], dist))
            distances.append((trainingSet[x], dist))
        distances.sort(key=operator.itemgetter(1))   # 把距离从小到大排列
        neighbors = []
        for x in range(k):   #排序完成后取前k个距离
            neighbors.append(distances[x][0])
        # print(neighbors)
        return neighbors


    def getResponse(self,neighbors):  # 根据少数服从多数，决定归类到哪一类
        classVotes = {}
        for x in range(len(neighbors)):
            response = neighbors[x][-1]  # 统计每一个分类的多少
            if response in classVotes:
                classVotes[response] += 1
            else:
                classVotes[response] = 1
        # print(classVotes.items())
        sortedVotes = sorted(classVotes.items(), key=operator.itemgetter(1), reverse=True) #reverse按降序的方式排列
        return sortedVotes[0][0]


    def getAccuracy(self,testSet, predictions):  # 准确率计算
        correct = 0
        pred_right = 0
        for x in range(len(testSet)):
            if testSet[x][-1] == predictions[x]:   #predictions是预测的和testset实际的比对
                correct += 1
            if predictions[x] == 1.0:
                pred_right += 1
                
        print('共有{}个预测正确，共有{}个测试数据'.format(correct, len(testSet)))
        print('pred_right:',pred_right)
        return (correct/float(len(testSet)))*100.0


    def getKnnResult(self, trainingSet, testInstance):
        k = 3
        type_length = 3
        neighbors = self.getNeighbors(trainingSet, testInstance, k, type_length)
        result = self.getResponse(neighbors)
        return result


    def Run(self):
        trainingSet = []
        testSet = []
        split = 0.75
        self.loadDataset(test_data, split, trainingSet, testSet)  # 数据划分
        print('Train set: ' + str(len(trainingSet)))
        print('Test set: ' + str(len(testSet)))
        print(trainingSet[:20])
        print(testSet[:20])
        #generate predictions
        predictions = []
        k = 3    # 取最近的3个数据
        # correct = []
        right=0
        for x in range(len(testSet)):  # 对所有的测试集进行测试
            if testSet[x][-1] == 1.0:
                right += 1
            neighbors = self.getNeighbors(trainingSet, testSet[x], k)   #找到3个最近的邻居
            result = self.getResponse(neighbors)    # 找这3个邻居归类到哪一类
            predictions.append(result)
            # print('predictions: ' + repr(predictions))
            # print('>predicted=' + repr(result) + ', actual=' + repr(testSet[x][-1]))
        # print(correct)
        accuracy = self.getAccuracy(testSet, predictions)
        print('test_right',right)
        print('Accuracy: ' + repr(accuracy) + '%')


if __name__ == '__main__':
    a = KNearestNeighbor()
    a.Run()


