# -*- coding: utf-8 -*-
"""
Created on Mon Oct 29 20:14:05 2018
@author: bird
对四路传感器进行数据采集。单击Start 按钮开始采集数据，单击backoff 回退数据，单击save，则会将采集到的数据进行存储
文件将会生成两种数据，其一是原始数据，其二是记录Index的记录数据，可根据Index将原始数据切割成所需要的若干种手势样本。
传感器数据格式为“0xxx1xxx2xxx3xxx”，开始第一位是是传感器序号，后面跟的是传感器数值。
"""

#!/usr/bin/python
# -*- coding: UTF-8 -*-

from Tkinter import *  #引入模块
import threading
import serial
import binascii
import os
import math
import tkMessageBox

global num,flag,f,f1,flagWriteData,cnum,startSaveStr,bakNameStr, gestureTypeStr, nameStr
num = 0
flag = 1
flagWriteData = 0
gestureTypeStr =''
nameStr =''
bakNameStr=''
serial_result = []
#波特率及串口号设置
ser = serial.Serial( #下面这些参数根据情况修改
  port='COM11',
  baudrate=115200,
)


cnum = []

isOpened = threading.Event()

def clear():
    global cnum,num
    cnum = []
    num = 0

def startSaveCB():
    global f,f1,flagWriteData,flag,startSaveStr, num, bakNameStr, gestureTypeStr, nameStr
    if startSaveStr.get()=='Start':
        print '****** Start '+gestureTypeStr+'th gesture type ******'
        # 判读输入的参数是否合法
        gestureTypeStr = gestureTypeEntry.get().strip()
        nameStr = nameEntry.get().strip()
        print '（username:'+ nameStr+', gesture type:'+gestureTypeStr+'）'
        if not(gestureTypeStr.isdigit()):
            print '请输入正确的gestureType'
            tkMessageBox.showinfo(title='Input Error!', message='Please input the integer type of the gesture type!')
            return
        if nameStr =='':
            print '请输入字符串型name'
            tkMessageBox.showinfo(title='Input Error!', message='Please input the string type of the name, which cannot be NULL!')
            return
        # 判断输入的用户是否已经输入数据，如果存在将提示用户是覆盖，还是结束
        clear() #清理全局变量
        if (bakNameStr!=nameStr):   # 如果更新了用户，将bakNameStr进行重新设置
            bakNameStr=''
            gestureTypeStr='1'
            gestureTypeEntry.delete(0, END) # 新用户手势将从1开始
            gestureTypeEntry.insert(0, gestureTypeStr)

        path = os.getcwd()
        new_path = os.path.join(path, nameStr)
        if (bakNameStr==''):
            if (not os.path.exists(new_path)):
                print '该用户第一次采集数据，产生新的文件夹'
                os.makedirs(new_path)
                bakNameStr = nameStr
            else:
                print '输入的用户的数据已经存在了，是否选择覆盖？'
                if not tkMessageBox.askyesno('Rewrite or Not?', 'File of current username exists! Do you want to rewrite them?'):
                    print '没有进行覆盖，这里我们要重新输入用户名'
                    tkMessageBox.showinfo(title='Rename the username or rename exsiting files！', message='Before continuing, please rename the username or rename exsiting files!')
                    return
                else:
                    print '选择了进行覆盖'
                    tkMessageBox.showinfo(title='Rewrite now！', message='Now the exsiting files will be rewrited!')
                    bakNameStr = nameStr
        file_name = gestureTypeStr + '_source.txt'
        f = open(path + '/' + nameStr + '/' + file_name, 'w')
        startSaveStr.set('Save') #改变该按钮的text
        startSaveButton.config(state='disabled')
        beginEndButton.configure(state='normal')

        # 开始打开进程，并开始使能写数据位进行数据写入文件
        isOpened.set()
        flagWriteData = 1
        #    com_thread.start()
        file_name1 = gestureTypeStr + '_begin_end.txt'
        f1 = open(path + '/' + nameStr + '/' + file_name1, 'w')
        flag = 1
        # 锁定输入栏，只有当保存数据后才将其解锁
        nameEntry.config(state='disabled')
        gestureTypeEntry.config(state='disabled')
        countLabel.config(text='开始采集第'+gestureTypeStr+'种手势')
    else:
        print '****** begin save '+str(gestureTypeStr)+'th gesture type ******'
        startSaveStr.set('Start')
        flag = 0
        flagWriteData = 0
        stopNum =0
        if len(cnum) % 2 == 0:
            stopNum = len(cnum)
        elif (len(cnum) % 2 == 1):  # cnum中只有奇数个，说明最后一个样本的endIndex没有记录
            stopNum = len(cnum) - 1
        for i in range(0, stopNum, 2):
            valStr = '' + str(cnum[i]) + '    ' + str(cnum[i + 1]) + '\n'
            f1.write(valStr)
        f.close()
        f1.close()
        clear()
        beginEndButton.config(state='disabled')
        backOffButton.config(state='disabled')
        # 保存好数据后将锁定的输入栏解锁
        nameEntry.config(state='normal')
        gestureTypeEntry.config(state='normal')
        gestureTypeEntry.delete(0, END)
        gestureTypeEntry.insert(0, '' + str(int(gestureTypeStr) + 1))
        countLabel.config(text='已保存第'+gestureTypeStr+'种手势数据')



def beginEndCB():
    global num
    if beginEndStr.get()=='Begin Index':
        beginEndStr.set('End Index')
        cnum.append(num)
        print '**增加样本** '+ '（username:'+ nameStr+', gesture type:'+gestureTypeStr+'）'+'；第'+ str(int(math.ceil(len(cnum) / 2.0))) + '样本:开始位置'
        countLabel.configure(text="开始第：" + bytes(int(math.ceil(len(cnum)/2.0))) + ' 个样本')
        if len(cnum)==1:
            backOffButton.config(state='normal')
        startSaveButton.config(state='disabled')  # 采集样本开始位置，这时候不能保存数据，必须采集了结束位置后才能保存
    else:
        beginEndStr.set('Begin Index')
        cnum.append(num)
        print '**增加样本** ' + '（username:' + nameStr + ', gesture type:' + gestureTypeStr + '）' + '；第' + str(int(math.ceil(len(cnum) / 2.0))) + '样本:结束位置'
        countLabel.configure(text="结束第：" + bytes(int(math.ceil(len(cnum)/2.0))) + ' 个样本')
        startSaveButton.config(state='normal')  # 采集样本开始位置，这时候不能保存数据，必须采集了结束位置后才能保存


def backOffCB():
    global num, flagWriteData
    if len(cnum)==0:
        backOffButton.config(state='disabled')
    else:
        if (len(cnum)%2==1): #如果该样本只进行了开始，直接将开始index删除，
            print '****删除样本**** ' + '（username:' + nameStr + ', gesture type:' + gestureTypeStr + '）' + '；第'  + str(int(math.ceil(len(cnum) / 2.0))) + '样本'
            cnum.pop()
            if len(cnum)==0:
                backOffButton.config(state='disabled')
                startSaveButton.config(state='disabled')
            else:
                startSaveButton.config(state='normal')
            countLabel.configure(text="重新开始第：" + bytes(int(math.ceil(len(cnum) / 2.0))+1) + ' 个样本')
            beginEndStr.set('Begin Index')
        else:
            print '****删除样本**** ' + '（username:' + nameStr + ', gesture type:' + gestureTypeStr + '）' + '；第'  + str(int(math.ceil(len(cnum) / 2.0))) + '样本'
            cnum.pop()
            cnum.pop()
            if len(cnum) == 0:
                backOffButton.config(state='disabled')
                startSaveButton.config(state='disabled')
            else:
                startSaveButton.config(state='normal')
            countLabel.configure(text="重新开始第：" + bytes(int(math.ceil(len(cnum) / 2.0))+1) + ' 个样本')
            beginEndStr.set('Begin Index')

def COMT():
    global num,flag,f
    print("trying connect to the serial^^^")
    while 1:
        n = ser.inWaiting()
        tmpN=n
        if n:
            #print n
            data = ''
            while n:
                data += str(binascii.b2a_hex(ser.read(1)))  # [2:-1]
                data += ' '
                n = n - 1
                #print data
            if data != '':
                if flagWriteData == 1:
                    f.write(data)
                    num = num + tmpN
                    print num


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
gestureTypeLabel=Label(top,text='手势类别:')
gestureTypeLabel.grid(row=1,column=0,sticky=E)
gestureTypeEntry=Entry(top)
gestureTypeEntry.grid(row=1,column=1)
gestureTypeEntry.insert(0,'1')
countLabel=Label(top,text='请输入采集者姓名和手势号')
countLabel.grid(row=0,column=2,columnspan=4,rowspan=2, sticky=E, padx=5, pady=5)

startSaveStr=StringVar()
startSaveButton=Button(top,textvariable=startSaveStr, width=15,command = startSaveCB)
startSaveButton.grid(row=2,column=0,rowspan=2)
startSaveStr.set('Start')

beginEndStr=StringVar()
beginEndButton=Button(top,textvariable=beginEndStr, width=15,command=beginEndCB, state='disabled')
beginEndButton.grid(row=2,column=1,rowspan=2)
beginEndStr.set('Begin Index')

backOffButton=Button(top,text='Back Off', width=15,command=backOffCB, state='disabled')
backOffButton.grid(row=2,column=3,rowspan=2)


# logFrame=LabelFrame(top)
# logText=Text(top,height=15,bg='green')
# logText.grid(row=6,column=0,rowspan=8,columnspan=4)
# #
# for i in range(1,10,1):
#     logText.insert(END,'hello')

com_thread = threading.Thread(target=COMT)
com_thread.setDaemon(True)
com_thread.start()

mainloop()
