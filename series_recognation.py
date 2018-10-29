# -*- coding: utf-8 -*-
"""
Created on Mon Oct 29 21:45:28 2018
加载采集好的手势数据，进行识别
@author: bird
"""

#!/usr/bin/python
# -*- coding: UTF-8 -*-

from Tkinter import *  #引入模块
import threading
import serial
import numpy as np
import csv
import time
import string
import binascii
import os
import math
import tkMessageBox
import time
import matplotlib.pyplot as plt
from sklearn import preprocessing
import string, sys, time, re, math, fileinput, glob, shutil
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
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from scipy import signal  

from sklearn.svm import SVC
model = SVC(C =1, kernel="linear")

global handGestureChangenum
handGestureChangenum = 0

global flag,f,flagWriteData,startSaveStr,bakNameStr, gestureTypeStr, nameStr,z,z1,z2,actflagzeroflag,data
global zeroCh1,zeroCh2,zeroCh3,zeroCh4,gesture
gesture = '???'
z = [[0 for i in range(400)] for i in range(4)]
z1 = [[],[],[],[]]
z2 = [[],[],[],[]]
zeroflag = 1
actflag = 0
flag = 1
flagWriteData = 0
gestureTypeStr =''
nameStr =''
bakNameStr=''
serial_result = []
# ser = serial.Serial( 
#   port = 'com11',
#   baudrate=115200,
# )
zeroCh1 = 0
zeroCh2 = 0
zeroCh3 = 0 
zeroCh4 = 0
#加载训练集，进行模型训练
global clf
datas = []
labels =[]
#'zyf-desk','zyf-air',,'jhx-air','jhx-desk','zk-air','zk-desk','wy-air','wy-desk','zxy-air','zxy-desk'
userNames=['zyf-desk','zyf-air','jhx-air','jhx-desk','zk-air','zk-desk','wy-air','wy-desk','zxy-air','zxy-desk'] #,'zxy1','zxy2','lh1','lh2''zyf1','zyf2','zyf3','zyf4','bhy1','bhy2','zxy1','zxy2','hjy1','hjy2','lh1','lh2','zxy3'
stopUser = []
print 'stopUser:',stopUser
stopClass = [] #4,5,7,1
print 'stopClass:',stopClass
for user in userNames:
    if not (user in stopUser):
        with open(user+"StaticFeature.txt") as ifile:
            for line in ifile:
                tokens = line.strip().split('\t')
                if not (int(tokens[0]) in stopClass):
                    datas.append([float(tk) for tk in tokens[1:]])
                    labels.append(int(tokens[0]))

print ('model process')
print len(x)
print len(y)           
x=np.array(datas)
y=np.array(labels)
clf = model.fit(x,y)

isOpened = threading.Event()

#----------------------------------------------------------------------
def actOrNot():#使用阈值判决当前静止还是运动
    global z2,actflag,handGestureChangenum
    A = 400
    if ((z2[0].max()-z2[0].min())>A)|((z2[1].max()-z2[1].min())>A)|((z2[2].max()-z2[2].min())>A)|((z2[3].max()-z2[3].min())>A):
        if actflag == 0:
            print (handGestureChangenum*4/3)
            actflag = 1
    else:
        actflag = 0
        
def zeroAutoUpdate():#参数基准自适应更新
    global zeroCh1,zeroCh2,zeroCh3,zeroCh4,z2,zeroflag

    zeroCh1 =z2[0].mean()
    zeroCh2 =z2[1].mean()
    zeroCh3 =z2[2].mean()
    zeroCh4 =z2[3].mean()

def staticDataProcess():#静态手势数据段特征提取
    global z2
    global zeroCh1,zeroCh2,zeroCh3,zeroCh4
    global sample
    sample = []
    mean1 =z2[0].mean()
    mean2 =z2[1].mean()
    mean3 =z2[2].mean()
    mean4 =z2[3].mean()
    fea1 = (mean1-zeroCh1)/4100
    fea2 = (mean2-zeroCh2)/4100
    fea3 = (mean3-zeroCh3)/4100
    fea4 = (mean4-zeroCh4)/4100
    chmax = max(mean1,mean2,mean3,mean4)
    fea5 = mean1/chmax
    fea6 = mean2/chmax
    fea7 = mean3/chmax
    fea8 = mean4/chmax
    a = [fea1,fea2,fea3,fea4,fea5,fea6,fea7,fea8]
    sample.append(a)

def staticRec():#静态手势识别
    global sample,clf,gesture
    gesture2 = gesture
    staticDataProcess()
    predict = clf.predict(sample)
    result = predict[0]
#     gestureTypeEntry.delete(0,END)
    if result == 1:
        gesture = '平'
#         zeroAutoUpdate()
    if result == 2:
        gesture = '上'
    if result == 3:
        gesture = '下'
    if result == 4:
        gesture = '左'
    if result == 5:
        gesture = '右'
    if gesture2 != gesture:
        print gesture
        print (handGestureChangenum*4/3)
#     gestureTypeEntry.delete(0,END)
#     gestureTypeEntry.insert(0,gesture)

def drawPic():#使用滑窗处理数据    
    global ch,z,z1,z2,actflag,zeroflag
    z= np.array(z)
    ch=np.array(ch)
#     print data
    lens = len(ch[1])
    z = np.hstack((z[:,lens:],ch))
    b,a = signal.butter(3,0.15,'low')  
    z2 = signal.filtfilt(b,a,z)
#     print z2
    if (z[0][0]!=0):
        if(zeroflag  == 1):
#             zeroAutoUpdate()
            zeroflag = 0
        else:
            actOrNot()
            if actflag == 0:
                staticRec()


#加载想要识别的手势动作序列
global flag,data
with open('./zk02.txt','rb') as f:
    start_time=time.time()
    while True:
        handGestureChangenum = handGestureChangenum + 8
        data=f.read(128)
        if len(data) > 120:
            ch = [[],[],[],[]]
            lens = int(len(data)/16)
            for i in range(16):
                if((data[i]=='0')&(data[i+4]=='1')&(data[i+8]=='2')&(data[i+12]=='3')):
                    break
            datas = data[i:i+16*lens]
            for j in range(lens):
                for chnum in range(4):
                    amplitude = int(datas[j*16+chnum*4+1],16)*256+int(datas[j*16+chnum*4+2],16)*16+int(datas[j*16+chnum*4+3],16)
                    ch[chnum].append(amplitude)
            drawPic()
        if  not data:
            print('cross_val_predict took %fs!' % (time.time() - start_time))
            break


print ('end')