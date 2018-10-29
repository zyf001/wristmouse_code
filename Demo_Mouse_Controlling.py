# -*- coding: utf-8 -*-
"""
Created on Mon Oct 29 21:56:19 2018
对手势进行实时识别，并控制鼠标进行上下左右移动
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
import pyautogui as pag
from scipy.interpolate import interp1d

from sklearn.svm import SVC
model = SVC(C =1.0, kernel="linear")

#全局参数定义

global flag,f,flagWriteData,startSaveStr,bakNameStr, gestureTypeStr, nameStr,z,z1,z2,actflagzeroflag,data
global zeroCh1,zeroCh2,zeroCh3,zeroCh4,gesture,flag_initial
gesture = '水平平放'
global dynamicFlag,dyz,dyz2
global n1

global realfram,realfram_last,sumEnergy
global dengyihui

dengyihui = 0


flag_initial = 0
realfram = 0
realfram_last = 0

n1 = 0

dynamicFlag = 0
z = [[0 for i in range(400)] for i in range(4)]
z1 = [[],[],[],[]]
z2 = [[],[],[],[]]
dyz = [[],[],[],[]]
dyz2 = [[],[],[],[]]
zeroflag = 1
actflag = 0
flag = 1
flagWriteData = 0
gestureTypeStr =''
nameStr =''
bakNameStr=''
serial_result = []
ser = serial.Serial( #波特率设置
  port = 'com11',
  baudrate=115200,
)
zeroCh1 = 0
zeroCh2 = 0
zeroCh3 = 0 
zeroCh4 = 0

#静态手势模型建立
global clf
datas = []
labels =[]
userNames=['zyf-air','zyf-desk'] #'jhx-air','jhx-desk','wy-air','wy-desk',,'zyf-air''zk-air',,','zk-desk'zyf-desk',,'wy-air','wy-desk','jhx-air','jhx-desk','zk-air','zk-desk''zyf''','zyf3','zyf1''zxy-air','zxy-desk',,'wy-air','wy-desk','zxy-air','zxy-desk','wy-air','wy-desk'
print userNames
stopUser = []
print 'stopUser:',stopUser
stopClass = [] #4,5,7,15
print 'stopClass:',stopClass
for user in userNames:
    if not (user in stopUser):
        with open(user+"StaticFeature.txt") as ifile:
            for line in ifile:
                tokens = line.strip().split('\t')
                if not (int(tokens[0]) in stopClass):
                    datas.append([float(tk) for tk in tokens[1:]])
                    labels.append(int(tokens[0]))
x=np.array(datas)
y=np.array(labels)
clf = model.fit(x,y)




isOpened = threading.Event()


#DTW函数-------------------------------------------------------------------

def dist_for_float(p1, p2) :
    dist = 0.0
    p1 = float(p1)
    p2 = float(p2)
    elem_type = type(p1)
    if  elem_type == float or elem_type == int :
        dist = float(abs(p1 - p2))
    else :
        sumval = 0.0
        for i in range(len(p1)) :
            sumval += pow(p1[i] - p2[i], 2)
        dist = pow(sumval, 0.5)
    return dist

def dtw(s1, s2, dist_func) :
    w = len(s1)
    h = len(s2)
    
    mat = [([[0, 0, 0, 0] for j in range(w)]) for i in range(h)]
    
    #print_matrix(mat)
    
    for x in range(w) :
        for y in range(h) :            
            dist = dist_func(s1[x], s2[y])
            mat[y][x] = [dist, 0, 0, 0]
            

    elem_0_0 = mat[0][0]
    elem_0_0[1] = elem_0_0[0] * 2
    for x in range(1, w) :
        mat[0][x][1] = mat[0][x][0] + mat[0][x - 1][1]
        mat[0][x][2] = x - 1
        mat[0][x][3] = 0
    for y in range(1, h) :
        mat[y][0][1] = mat[y][0][0] + mat[y - 1][0][1]            
        mat[y][0][2] = 0
        mat[y][0][3] = y - 1
    for y in range(1, h) :
        for x in range(1, w) :
            distlist = [mat[y][x - 1][1], mat[y - 1][x][1], 2 * mat[y - 1][x - 1][1]]
            mindist = min(distlist)
            idx = distlist.index(mindist)
            mat[y][x][1] = mat[y][x][0] + mindist
            if idx == 0 :
                mat[y][x][2] = x - 1
                mat[y][x][3] = y
            elif idx == 1 :
                mat[y][x][2] = x
                mat[y][x][3] = y - 1
            else :
                mat[y][x][2] = x - 1
                mat[y][x][3] = y - 1
    result = mat[h - 1][w - 1]
    retval = result[1]
    path = [(w - 1, h - 1)]
    while True :
        x = result[2]
        y = result[3]
        path.append((x, y))

        result = mat[y][x]
        if x == 0 and y == 0 :
            break
    return retval, sorted(path)

def display(s1, s2) :
    val, path = dtw(s1, s2, dist_for_float)
    
    w = len(s1)
    h = len(s2)
    
    mat = [[1] * w for i in range(h)]
    for node in path :
        x, y = node
        mat[y][x] = 0
    mat = np.array(mat)
    return val

def dtwSamplePrecess(SourceSample=[2,5,2],Length = 10):
    SampleList = []
    xx = np.linspace(0,len(SourceSample) , Length)
    x = np.linspace(0, len(SourceSample), len(SourceSample))
    f = interp1d(x, SourceSample,'slinear')
    ynew = f(xx)
    return np.array(ynew)

def readFile(desPath):
    z = []
    data = open(desPath)
    for each_line in data:
        a = each_line.split(" ")
        b = a[:-1]
        z.append(b)
    z = [[float(x) for x in inner] for inner in z]
    z = np.array(z)
    return z[0]

SingleTapTemplate = readFile('single.txt')
DoubleTapTemplate = readFile('double.txt')
# print SingleTapTemplate

#----------------------------------------------------------------------


def actOrNot():#当前时间窗内手部是否运动
    global z2,actflag,realfram,realfram_last,gesture
    if gesture =='水平平放':
        A=400
    else:
        A=700
    if ((z2[0].max()-z2[0].min())>A)|((z2[1].max()-z2[1].min())>A)|((z2[2].max()-z2[2].min())>A)|((z2[3].max()-z2[3].min())>A):
        if ((realfram-realfram_last)>300):
            resultTypeEntry.delete(0,END)
            resultTypeEntry.insert(0,'运动中')
            actflag = 1
            realfram_last = realfram
        
    else: 
        if ((realfram-realfram_last)>300):
            resultTypeEntry.delete(0,END)
            resultTypeEntry.insert(0,'静止中')
            actflag = 0
        
def zeroAutoUpdate():#压力参数更新
    global zeroCh1,zeroCh2,zeroCh3,zeroCh4,z2,zeroflag

    zeroCh1 =z2[0].mean()
    zeroCh2 =z2[1].mean()
    zeroCh3 =z2[2].mean()
    zeroCh4 =z2[3].mean()

def staticDataProcess():#静态数据处理
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

def dynamicDataProcess():#动态数据处理
    global dyz2
    global dysample,sumEnergy
    dysample = []
    c0  = dyz2[0][0]
    c1  = dyz2[1][0]
    c2  = dyz2[2][0]
    c3  = dyz2[3][0]
    ch3 = [[], [], [], []]
    ch3[0] = (dyz2[0]-c0)/1000
    ch3[1] = (dyz2[1]-c1)/1000
    ch3[2] = (dyz2[2]-c2)/1000
    ch3[3] = (dyz2[3]-c3)/1000
    energy1 = 0
    energy2 = 0
    energy3 = 0
    energy4 = 0
    length = len(ch3[0])
    for i in range(length):
        energy1 = energy1 + ch3[0][i]*ch3[0][i]
        energy2 = energy2 + ch3[1][i]*ch3[1][i]
        energy3 = energy3 + ch3[2][i]*ch3[2][i]
        energy4 = energy4 + ch3[3][i]*ch3[3][i]
    sumEnergy = energy1+energy2+energy3+energy4

    dysample=dtwSamplePrecess(dyz2[2],100)
    c0  = min(dysample)
    dysample = dysample - c0
    dysample = dysample/float(max(dysample))
    dysample =dysample[:80]
    if (sumEnergy>500):#
        dysample=[]


#动态手势识别
def dynamicRec():#阈值定为50
    global dysample,dyclf,gesture,sumEnergy
    dynamicDataProcess()
    gesture2 = '未知'
    if dysample != []:
#         print dysample
        dist1 = float(display(dysample, SingleTapTemplate))
        dist2 = float(display(dysample, DoubleTapTemplate))
        if gesture =='水平平放':
            if dist1 < dist2:
                if sumEnergy<100:
                    gesture2 = '左键单击'
                    pag.click()
                else:
                    gesture2 = '右键单击'
                    pag.rightClick()
#                 print sumEnergy
#                 pag.click()

            if dist1 > dist2:
                gesture2 = '双击'
                pag.doubleClick()
            
#                 pag.click()

        dynamicGestureTypeEntry.delete(0,END)
        dynamicGestureTypeEntry.insert(0,gesture2)  
    
def staticRec():#静态手势识别
    global sample,clf,gesture,n1,flag_initial
    staticDataProcess()
    predict = clf.predict(sample)
    result = predict[0]
    gesture2 = gesture
    gestureTypeEntry.delete(0,END)
    if result == 1:
        gesture = '水平平放'
        if flag_initial < 4:
            zeroAutoUpdate()
            flag_initial = flag_initial + 1
            print flag_initial
    if result == 2:
        gesture = '向上'
    if result == 3:
        gesture = '向下'
    if result == 4:
        gesture = '向左'
    if result == 5:
        gesture = '向右'
    if gesture2 == gesture:
#         print n1
        n1 = n1 +1
        if n1 > 0:    
#             print currentMouseX
#             print currentMouseY
            if gesture == '向上':
                pag.moveRel(0, -5*n1,0.2)
            if gesture == '向下':
                pag.moveRel(0, 5*n1,0.2)
            if gesture == '向左':
                pag.moveRel(-5*n1, 0,0.2)
            if gesture == '向右':
                pag.moveRel(5*n1, 0,0.2)
#             n1 =0
    else:
        n1 = 0    
    gestureTypeEntry.delete(0,END)
    gestureTypeEntry.insert(0,gesture)

def drawPic():    
#获取GUI界面上的参数
    global ch,z,z1,z2,actflag,zeroflag,dyz,dyz2,dynamicFlag,realfram,dengyihui
    z= np.array(z)
    ch=np.array(ch)
    lens = len(ch[1])
    realfram = realfram + lens
    z = np.hstack((z[:,lens:],ch))
    if dynamicFlag == 0:
        dyz = z
    else:
        dyz = np.hstack((dyz,ch))
    b,a = signal.butter(3,0.15,'low')  
    z2 = signal.filtfilt(b,a,z)  
    if (z[0][0]!=0)&zeroflag:
        zeroAutoUpdate()
        zeroflag = 0
    actOrNot()
    dengyihui = dengyihui + 1
    if actflag == 0:
        if dynamicFlag == 1:
            dyz2 = signal.filtfilt(b,a,dyz)  
            dynamicFlag = 0
            dynamicRec()
            dengyihui = 0
        if (dengyihui>30)|(gesture=='水平平放'):
            staticRec()
    else:
        dynamicFlag = 1
        


def COMT(): #串口采集

    global flag,f,data
    print("trying connect to the serial^^^")
    while 1:
        n = ser.inWaiting()
        tmpN=n
        if n:
            #print n
            data = ''
            while n:
                data += str(binascii.b2a_hex(ser.read(1)))  # [2:-1]
#                 data += ' '
                n = n - 1
#                 print data
            if data != '':
                if flagWriteData == 1:
                    f.write(data)
#                     print num


def DISPLAY():  #使用标志位来判定是否

    global data,ch
    data1 = ''
    flag = 0
    while 1:
        if data != '':
            if data != data1:
                if flag == 0:
                    if len(data) < 20:
                        flag =1
                if flag == 1:
                    if len(data) > 120:
                        ch = [[],[],[],[]]
                        lens = int(len(data)/16) - 1
                        for i in range(16):
                            if((data[i]=='0')&(data[i+4]=='1')&(data[i+8]=='2')&(data[i+12]=='3')):
                                break
                        flag =0
                        datas = data[i:i+16*lens]
                        for j in range(lens):
                            for chnum in range(4):
                                amplitude = int(datas[j*16+chnum*4+1],16)*256+int(datas[j*16+chnum*4+2],16)*16+int(datas[j*16+chnum*4+3],16)
                                ch[chnum].append(amplitude)
                        drawPic()
                data1 = data

#config函数就是通过设置组件的参数来改变组件的，这里改变的是font字体大小
top=Tk()   #主窗口
top.geometry('600x400')  #设置了主窗口的初始大小600x400
frame = Frame(top)
u = StringVar()
top.title('Ubicom gesture recognition ')
resultTypeLabel=Label(top,text='result:')
resultTypeLabel.grid(row=5,column=0,sticky=E)
resultTypeEntry=Entry(top)
resultTypeEntry.grid(row=5,column=1)
resultTypeEntry.insert(0,'working')
gestureTypeLabel=Label(top,text='staticgesture:')
gestureTypeLabel.grid(row=10,column=0,sticky=E)
gestureTypeEntry=Entry(top)
gestureTypeEntry.grid(row=10,column=1)
gestureTypeEntry.insert(0,'palmup')

dynamicGestureTypeLabel=Label(top,text='dynamicGesture:')
dynamicGestureTypeLabel.grid(row=15,column=0,sticky=E)
dynamicGestureTypeEntry=Entry(top)
dynamicGestureTypeEntry.grid(row=15,column=1)
dynamicGestureTypeEntry.insert(0,'No')

com_thread = threading.Thread(target=COMT)
com_thread.setDaemon(True)
com_thread.start()


display_thread = threading.Thread(target=DISPLAY)
display_thread.setDaemon(True)
display_thread.start()
mainloop()
