# -*- coding: utf-8 -*-
"""
Created on Mon Oct 29 21:43:12 2018
十折交叉验证验证算法性能
@author: bird
"""

# -*- coding: utf-8 -*-
import numpy as np
import scipy as sp
import time
import matplotlib.pyplot as plt
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_predict
from sklearn import metrics
from sklearn import svm
from sklearn import preprocessing
import random
# 各种分类函数

# liu SVM Classifier
def lsvm_classifier():
    from sklearn.svm import SVC
    model = SVC(C =1.0, kernel="linear")
    return model

#zhang SVM classifier
def zsvm_classifier():
    from sklearn import svm
    model = svm.OneClassSVM(nu=0.1, kernel="rbf", gamma=0.1)
    return model

# Multinomial Naive Bayes Classifier
def naive_bayes_classifier():
    from sklearn.naive_bayes import MultinomialNB
    model = MultinomialNB(alpha=0.01)
    return model

# Logistic Regression Classifier
def logistic_regression_classifier():
    from sklearn.linear_model import LogisticRegression
    model = LogisticRegression(penalty='l2')
    return model

# KNN Classifier
def knn_classifier():
    from sklearn.neighbors import KNeighborsClassifier
    model = KNeighborsClassifier()
    return model

# Random Forest Classifier
def random_forest_classifier():
    from sklearn.ensemble import RandomForestClassifier
    model = RandomForestClassifier(n_estimators=10)
    return model

# Decision Tree Classifier
def decision_tree_classifier():
    from sklearn import tree
    model = tree.DecisionTreeClassifier()
    return model

#Decision Tree Regressor

def decision_tree_regression():
    from sklearn import tree
    model = tree.DecisionTreeRegressor()
    return model

#multi-layer perceptron

def multi_layer_perceptron():
    from sklearn.neural_network import MLPClassifier
    model =  MLPClassifier(solver='lbfgs', alpha=1e-5,
                           hidden_layer_sizes=(100), random_state=1)
    return model
#NearestNeighbors
def nearest_neighbors():
    from sklearn import neighbors
    model = neighbors.KNeighborsClassifier(3, 'distance')
    return model


## 将数据保存为数组形式
def random_shuffle_data(data,labels,seedNum):
    random.seed(seedNum)
    ind=range(0,len(data),1)
    random.shuffle(ind)
    shuffleData=[]
    shuffleLabels=[]
    for i in ind:
        shuffleData.append(data[i])
        shuffleLabels.append(labels[i])
    return shuffleData,shuffleLabels


if __name__ == '__main__':
    print('begin myclassifier')
    data = []
    labels =[]
    userNames=['zyf-desk','zyf-air','zxy-air','zxy-desk','jhx-air','jhx-desk','wy-air','wy-desk','zk-air','zk-desk'] #,'zyf','zyf1','zyf2','zyf3','zyf4','bhy1','bhy2','zxy1','zxy2'
    print userNames
    stopUser = []
    print 'stopUser:',stopUser
    stopClass = [] #4,5,7,15
    print 'stopClass:',stopClass
    for user in userNames:
        if not (user in stopUser):
            with open(user+"StaticFeature_Wristflex.txt") as ifile:#_com
                for line in ifile:
                    tokens = line.strip().split('\t')
                    if not (int(tokens[0]) in stopClass):
                        data.append([float(tk) for tk in tokens[1:]])
                        labels.append(int(tokens[0]))
    ## 对数据进行随机排序，相同随即种子具有相同的随机排序结果
    (data,labels)=random_shuffle_data(data,labels,1)


    x=np.array(data)
    y=np.array(labels)
    print x[1]
    ## 数据预处理：归一化处理
    #minMaxScale=preprocessing.MinMaxScaler()
    #x=minMaxScale.fit_transform(x)
    #print(minMaxScale.fit_transform(x))


    test_classifiers = ['NN','KNN', 'LR', 'RF', 'DT','DR','MLP','zsvm','lSVM']#,'NB', 'LR', 'RF', 'DT','DR','MLP','zsvm',,'NB'

    classifiers = {
                    'lSVM': lsvm_classifier,
                    'NB': naive_bayes_classifier,
                    'KNN': knn_classifier,
                    'LR': logistic_regression_classifier,
                    'RF': random_forest_classifier,
                    'DT': decision_tree_classifier,
                    'DR': decision_tree_regression,
                    'MLP': multi_layer_perceptron,
                    'NN': nearest_neighbors,
                    'zsvm': zsvm_classifier
                   }

    # 测试交叉验证
    # KFoldNum=6
    # X_train, X_test, y_train, y_test=train_test_split(x,y,test_size=1.0/KFoldNum,random_state=1)
    # model = classifiers['SVM']()
    # clf=model.fit(X_train,y_train)
    # print clf.score(X_test,y_test)
    ## 使用不同分类方法对实验数据进行仿真
    misNumPerClass = {} #存储不同类别的各自错误数
    classNum = 5

    for classifier in test_classifiers:
        for i in range(1,classNum+1,1):
            misNumPerClass[i] = 0

        print('******************* %s ********************' % classifier)
        start_time=time.time()
        model=classifiers[classifier]()
        predict = cross_val_predict(model, x, y, cv=10)
        print('cross_val_predict took %fs!' % (time.time() - start_time))
        accuracy=metrics.accuracy_score(y,predict)
        print len(y)
        for i in range(0,len(y),1):
            if not y[i]==predict[i]:
                misNumPerClass[y[i]]+=1
        print misNumPerClass
        print('accuracy: %.2f%%' % (100 * accuracy))
