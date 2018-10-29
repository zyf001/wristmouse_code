"""
Created on Mon Oct 29 20:27:42 2018

@author: bird
实时展示传感器数据波形情况。
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
import random
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from scipy import signal  


from sklearn import tree
model = tree.DecisionTreeRegressor()
stopClass = []

global num,flag,f,f1,f2,f3,flagWriteData,cnum,startSaveStr,bakNameStr, gestureTypeStr, nameStr,z,actflag1,z1,z2,actflag2,actflag3,zz,data
z = [[0 for i in range(300)] for i in range(4)]
z1 = [[],[],[],[]]
z2 = [[],[],[],[]]
zz = [[],[],[],[]]
num = 0
flag = 1
flagWriteData = 0
gestureTypeStr =''
nameStr =''
bakNameStr=''
serial_result = []
actflag1 = 0
actflag2 = 1
actflag3 = 300
ser = serial.Serial( 
  port = 'com11',
  baudrate=115200,
)



cnum = []

isOpened = threading.Event()

#----------------------------------------------------------------------
def drawPic():    
#获取GUI界面上的参数
    global ch,z,actflag1,c1,c2,c3,c4,z1,z2,actflag2,actflag3,zz,mean0,mean1,mean2,mean3

    z= np.array(z)
    ch=np.array(ch)
    lens = len(ch[1])
    z = np.hstack((z[:,lens:],ch))
    b,a = signal.butter(3,0.15,'low')  
    z2 = signal.filtfilt(b,a,z)  
    #清空图像，以使得前后两次绘制的图像不会重叠
    drawPic.f.clf()
    drawPic.a=drawPic.f.add_subplot(111) 
    drawPic.a.plot(z2[0],'b')
    drawPic.a.plot(z2[1],'r')
    drawPic.a.plot(z2[2],'g')
    drawPic.a.plot(z2[3],'y')
    drawPic.a.set_title('Demo: Draw N Random Dot')
    drawPic.canvas.show()
   

def clear():
    global cnum,num
    cnum = []
    num = 0

def COMT():

    global num,flag,f,data
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
                    num = num + tmpN
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
top.title('Ubicom 手势数据采集 ')
nameLabel=Label(top,text='姓名:')
nameLabel.grid(row=0,sticky=E)
nameEntry=Entry(top)
nameEntry.grid(row=0,column=1)
nameEntry.insert(0,'zyf')
gestureTypeLabel=Label(top,text='手势类别:')
gestureTypeLabel.grid(row=1,column=0,sticky=E)
resultTypeLabel=Label(top,text='result:')
resultTypeLabel.grid(row=5,column=0,sticky=E)
resultTypeEntry=Entry(top)
resultTypeEntry.grid(row=5,column=1)
resultTypeEntry.insert(0,'???')
gestureTypeEntry=Entry(top)
gestureTypeEntry.grid(row=1,column=1)
gestureTypeEntry.insert(0,'1')
countLabel=Label(top,text='请输入采集者姓名和手势号')
countLabel.grid(row=0,column=2,columnspan=4,rowspan=2, sticky=E, padx=5, pady=5)

startSaveStr=StringVar()
startSaveButton=Button(top,textvariable=startSaveStr, width=15,command = startSaveCB)
startSaveButton.grid(row=2,column=2,rowspan=2)
startSaveStr.set('Start')

#在Tk的GUI上放置一个画布，并用.grid()来调整布局
drawPic.f = Figure(figsize=(5,4), dpi=100) 
drawPic.canvas = FigureCanvasTkAgg(drawPic.f, master=top)
drawPic.canvas.show()
drawPic.canvas.get_tk_widget().grid(row=11, columnspan=3)    

com_thread = threading.Thread(target=COMT)
com_thread.setDaemon(True)
com_thread.start()


display_thread = threading.Thread(target=DISPLAY)
display_thread.setDaemon(True)
display_thread.start()
mainloop()
