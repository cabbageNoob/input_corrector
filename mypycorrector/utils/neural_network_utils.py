'''
@Descripttion: 
@version: 
@Author: cjh <492795090@qq.com>
@Date: 2020-04-09 09:38:45
@LastEditors: cjh <492795090@qq.com>
@LastEditTime: 2020-04-24 09:46:57
'''
# -*- coding: utf-8 -*-
import csv
import random
import os, sys
from sklearn.metrics import accuracy_score
import torch.nn.functional as F
import torch.nn as nn
# import matplotlib.pyplot as plt
import sklearn.datasets
import torch
import numpy as np
np.random.seed(0)

pwd_path = os.path.abspath(os.path.dirname(__file__))
test_data = os.path.join(pwd_path, '../data/cn/sighan/score_data/score_data_segment.txt')


def loadDataset(filename, split, training_X, training_y, test_X, test_y):
    with open(filename, 'r', encoding='utf8') as csvfile:
        lines = csv.reader(csvfile)  # 读取所有的行
        dataset = list(lines)  # 转化成列表
        data_y = list()
        for x in range(len(dataset) - 1):
            temp = list()
            for y in range(3):
                print(float(dataset[x][y + 2]))
                temp.append(float(dataset[x][y + 2]))
            # data_X.append(temp)
            data_y.append(int(dataset[x][-1]))
            if random.random() < split:   # 将所有数据加载到train和test中
                training_X.append(temp)
                training_y.append(data_y[x])
            else:
                test_X.append(temp)
                test_y.append(data_y[x])
    training_X = torch.Tensor(training_X).type(torch.FloatTensor)
    training_y = torch.Tensor(training_y).type(torch.LongTensor)
    test_X = torch.Tensor(test_X).type(torch.FloatTensor)
    test_y = torch.Tensor(test_y).type(torch.LongTensor)
    return training_X, training_y, test_X, test_y


#our class must extend nn.Module

class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        #Our network consists of 3 layers. 1 input, 1 hidden and 1 output layer
        #This applies Linear transformation to input data.
        self.fc1 = nn.Linear(3, 4)

        #This applies linear transformation to produce output data
        self.fc2 = nn.Linear(4, 2)

    #This must be implemented
    def forward(self, x):
        #Output of the first layer
        x = self.fc1(x)
        #Activation function is Relu. Feel free to experiment with this
        x = torch.tanh(x)
        #This produces output
        x = self.fc2(x)
        return x

    #This function takes an input and predicts the class, (0 or 1)
    def predict(self, x):
        #Apply softmax to output
        pred = F.softmax(self.forward(x))
        ans = []
        for t in pred:
            if t[0] > t[1]:
                ans.append(0)
            else:
                ans.append(1)
        return torch.tensor(ans)


def make_save_model(training_X,training_y):
    #Initialize the model
    model = Net()
    #Define loss criterion
    criterion = nn.CrossEntropyLoss()
    #Define the optimizer
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

    #Number of epochs
    epochs = 50000
    #List to store losses
    losses = []
    for i in range(epochs):
        #Precit the output for Given input
        y_pred = model.forward(training_X)
        #Compute Cross entropy loss
        loss = criterion(y_pred, training_y)
        #Add loss to the list
        losses.append(loss.item())
        #Clear the previous gradients
        optimizer.zero_grad()
        #Compute gradients
        loss.backward()
        #Adjust weights
        optimizer.step()
    torch.save(model, 'network_segment.pth')  # 保存整个网络
    print(accuracy_score(model.predict(training_X), training_y))

def load_model(model_path):
    network_whole = torch.load(model_path)
    return network_whole

def predict(x):
    x = torch.from_numpy(x).type(torch.FloatTensor)
    ans = model.predict(x)
    return ans.numpy()

# Helper function to plot a decision boundary.
# If you don't fully understand this function don't worry, it just generates the contour plot below.
def plot_decision_boundary(pred_func, X, y):
    # Set min and max values and give it some padding
    x_min, x_max = X[:, 0].min() - .5, X[:, 0].max() + .5
    y_min, y_max = X[:, 1].min() - .5, X[:, 1].max() + .5
    h = 0.01
    # Generate a grid of points with distance h between them
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
                         np.arange(y_min, y_max, h))
    # Predict the function value for the whole gid
    Z = pred_func(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)
    # Plot the contour and training examples
    plt.contourf(xx, yy, Z, cmap=plt.cm.Spectral)
    plt.scatter(X[:, 0], X[:, 1], c=y, cmap=plt.cm.binary)
    plt.show()

def run():
    training_X = []
    training_y = []
    test_X = []
    test_y = []
    split = 1.0
    training_X, training_y, test_X, test_y=loadDataset(
        test_data, split, training_X, training_y, test_X, test_y)
    make_save_model(training_X, training_y)


if __name__ == '__main__':
    # network_whole = load_model()
    # print(accuracy_score(network_whole.predict(X), y))
    run()
    # training_X = []
    # training_y = []
    # test_X = []
    # test_y = []
    # split = 0.5
    # training_X, training_y, test_X, test_y = loadDataset(
    #     test_data, split, training_X, training_y, test_X, test_y)
    # model = load_model('network_new.pth')
    # print(accuracy_score(model.predict(test_X), test_y))