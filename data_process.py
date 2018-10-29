# -*- coding: utf-8 -*-
"""
Created on Mon Oct 29 20:35:21 2018
处理我们采集到的数据，并进行相应的特征提取
@author: bird
"""

#!/usr/bin/python
# -*- coding: UTF-8 -*-
#dynamic gesture
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
from __future__ import division 


#设置所需要遍历的名称空间
fff = [[''],['wy-air','wy-desk'],['zyf-air','zyf-desk'],['zk-air','zk-desk'],['zxy-air','zxy-desk'],['jhx-air','jhx-desk']]
#当前遍历的的用户及场景
user_ids = 1
user = fff[user_ids][1]

#遍历原始数据，将其切割成一个个的小样本
username = user + '/'
for names in range(9):
    foldname = str(names + 1)#
    for zz in range(1):
        data = []
        data1 = []
        str1 = ''
        f3path = 'C:/Users/bird/'+username+foldname+'/'+str(zz+1)+'.txt'
        f3 = open(f3path, 'r')
        testpath = 'C:/Users/bird/'+username+foldname+'/'+user+str(zz+1)+'.txt'
        f2 = open(testpath, 'w+')
        ss = f3.read()
        f3.close()
        for qqq in range(100):
            if (ss[qqq] != ' '):
                if ((int(ss[qqq], 16) == 0) & (int(ss[qqq + 6], 16) == 1) & (int(ss[qqq + 12], 16) == 2) & (
                    int(ss[qqq + 18], 16) == 3) ):
                    break
        for z in range(qqq, (len(ss) - 1)):
            if (ss[z] != ' '):
                data1.append(ss[z])
        length = len(data1)
        lennum = int(length / 16)
        for j in range(lennum):
            data.append(data1[16 * j:16 * j + 16])
        for dsx in data:
            for esx in dsx:
                str1 = str1 + str(esx)
        f2.write(str1)
        f2.close()
global username
global zeroCh1,zeroCh2,zeroCh3,zeroCh4
global testpath,featpath,testpath1
global fea1,fea2,fea3,fea4,fea5,fea6,fea7,fea8
global channel1,channel2,channel3,channel4

zeroCh1 = 0
zeroCh2 = 0
zeroCh3 = 0 
zeroCh4 = 0


def zeroCh():#根据上一次为平放的手势做一个归一化，即我们的压力参数自适应策略
    global zeroCh1,zeroCh2,zeroCh3,zeroCh4
    global testpath1
    j = 0
    ch1 = [[], [], [], []]
    f4 = open(testpath1, 'r')
    sss = f4.read()
    f4.close()
    length = len(sss)
    lennum = int(length / 4)
    franum = int(length / 16)
    for z in range(lennum):
        num = (int(sss[4 * z + 1], 16) * 16 * 16) + (int(sss[4 * z + 2], 16) * 16) + int(sss[4 * z + 3], 16)
        ch1[j].append(num)
        j = j + 1
        if j == 4:
            j = 0
    ch1 = np.array(ch1)
    zeroCh1 =ch1[0].mean()
    zeroCh2 =ch1[1].mean()
    zeroCh3 =ch1[2].mean()
    zeroCh4 =ch1[3].mean()
    
def featureExtract(): #特征提取
    global zeroCh1,zeroCh2,zeroCh3,zeroCh4
    global fea1,fea2,fea3,fea4,fea5,fea6,fea7,fea8
    global channel1,channel2,channel3,channel4
    mean1 = channel1.mean()
    mean2 = channel2.mean()
    mean3 = channel3.mean()
    mean4 = channel4.mean()
#   时域特征：和参考值相比的变化程度
#     fea1 = (mean1-zeroCh1)/4100  #使用自更新策略
#     fea2 = (mean2-zeroCh2)/4100  #使用自更新策略
#     fea3 = (mean3-zeroCh3)/4100  #使用自更新策略
#     fea4 = (mean4-zeroCh4)/4100  #使用自更新策略
    fea1 = (mean1)/4100  #不使用自更新策略
    fea2 = (mean2)/4100  #不使用自更新策略
    fea3 = (mean3)/4100  #不使用自更新策略
    fea4 = (mean4)/4100  #不使用自更新策略
    chmax = max(mean1,mean2,mean3,mean4)
#空间域特征，各传感器之间的相互大小比较
    fea5 = mean1/chmax
    fea6 = mean2/chmax
    fea7 = mean3/chmax
    fea8 = mean4/chmax

def dataProcess():#将提取到的特征数据存储到文件中
    global testpath,featpath
    global fea1,fea2,fea3,fea4,fea5,fea6,fea7,fea8
    global channel1,channel2,channel3,channel4
    j = 0
    ch = [[], [], [], []]
    f3 = open(testpath, 'r')
    ss = f3.read()
    f3.close()
    length = len(ss)
    lennum = int(length / 4)
    franum = int(length / 16)
    for z in range(lennum):
        num = (int(ss[4 * z + 1], 16) * 16 * 16) + (int(ss[4 * z + 2], 16) * 16) + int(ss[4 * z + 3], 16)
        ch[j].append(num)
        j = j + 1
        if j == 4:
            j = 0
    ch = np.array(ch)
    samplenum =  int(franum/200)-1
    print samplenum
    f1 = open(featpath,'w+')
    for samplenumber in range(samplenum):
        channel1 = ch[0][(samplenumber*200):(samplenumber*200+200)]
        channel2 = ch[1][(samplenumber*200):(samplenumber*200+200)]
        channel3 = ch[2][(samplenumber*200):(samplenumber*200+200)]
        channel4 = ch[3][(samplenumber*200):(samplenumber*200+200)]
        featureExtract()
        #f1.write(str(foldname+2)+'\t') #手势识别
        f1.write(str(user_ids)+'\t') #用户识别
        f1.write(str(fea1)+ '\t')
        f1.write(str(fea2)+ '\t')
        f1.write(str(fea3)+ '\t')
        f1.write(str(fea4)+ '\t')
        f1.write(str(fea5)+ '\t')
        f1.write(str(fea6)+ '\t')
        f1.write(str(fea7)+ '\t')
        f1.write(str(fea8)+ '\t\n')
    f1.close()

for foldname in range(4):
    testpath =  'C:/Users/bird/'+username +str(2*(foldname+1))+'/'+user+'1.txt'
    testpath1 = 'C:/Users/bird/'+ username +str(2*(foldname+1)-1)+'/'+user+'1.txt'
    featpath =  'C:/Users/bird/'+username +str(2*(foldname+1))+'/'+str(2*(foldname+1))+'_1_feat.txt'
    print featpath
    zeroCh()
    dataProcess()


    
stagesture = 'C:/Users/bird/'+username + user+'StaticFeature_identification.txt'
f1 = open(stagesture,'w+')
for i in range(8):
    sample =  'C:/Users/bird/'+username+str(i+2)+'/'+str(i+2)+'_1_feat.txt'
    f2 = open(sample, 'r')
    ss = f2.read()
    f2.close()
    f1.write(ss)
f1.close()
