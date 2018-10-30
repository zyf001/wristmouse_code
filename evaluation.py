# -*- coding: utf-8 -*-
"""
Created on Tue Oct 30 09:11:59 2018
TEST_MOVE
评估手环性能的小程序
移动鼠标点击红色方块，共计五轮，记录移动和点击方块所需要花费的时间。
@author: bird
"""

from Tkinter import *
import threading  
import time
import datetime  
global oldtime,newtime
 
    
    
global test_event 

test_event = 0
 
def call_back(event):
    # 按哪个键，在Shell中打印
    global root,test_event,w,h,oldtime
    print("the location of now ", event.x, event.y)
#     root['bg'] = 'red'
#记录不同阶段操作，所需要消耗的时间
    if (event.x<=50)&(event.y<=50):
        test_event = 1
        newtime=datetime.datetime.now()  
        print u'相差：%s秒'%(newtime-oldtime).seconds 
    if test_event == 1:
        if (event.x>=(w-50))&(event.y>=(h-50)):
            test_event = 2
            newtime=datetime.datetime.now()  
            print u'相差：%s秒'%(newtime-oldtime).seconds 
    if test_event == 2:
        if (event.x<=50)&(event.y>=(h-50)):
            test_event = 3
            newtime=datetime.datetime.now()  
            print u'相差：%s秒'%(newtime-oldtime).seconds 
    if test_event == 3:
        if (event.x>=(w-50))&(event.y<=50):
            test_event = 4
            newtime=datetime.datetime.now()  
            print u'相差：%s秒'%(newtime-oldtime).seconds 
    if test_event == 4:
        if (event.x>=(w/2-25))&(event.y<=h/2+25)&(event.x<=(w/2+25))&(event.y>=h/2-25):
            newtime=datetime.datetime.now()  
            print u'相差：%s秒'%(newtime-oldtime).seconds 
            print "end"
    rec()

def click():#定义单击事件
    global root
    root.bind("<Button>", call_back)

    
def rec():#改变红色小方块出现的位置
    global root,test_event,cv,sel,w,h
    if test_event == 1:
        cv.coords(sel,(w-50,h-50,w,h))
    if test_event == 2:
        cv.coords(sel,(0,h-50,50,h))
    if test_event == 3:
        cv.coords(sel,(w-50,0,w,50))
    if test_event == 4:
        cv.coords(sel,(w/2-25,h/2-25,w/2+25,h/2+25))
 
 
def main():
    global root,cv,sel,w,h,oldtime
    root = Tk()
    w = root.winfo_screenwidth()-20
    h = root.winfo_screenheight()-40
    print w,h
    root.geometry("%dx%d" %(w,h))
    root.attributes("-topmost",True)
    
    
    t1 = threading.Thread(target=click,args=(),name='thread-refresh') 
    t1.setDaemon(True) 
    t1.start() 
    cv = Canvas(root, width = w, height = h, bg = "black")
    sel = cv.create_rectangle(0,0,50,50,outline='blue',fill='red')
    cv.pack()
    oldtime=datetime.datetime.now()  
    
    mainloop()
 
if __name__ == '__main__':
    main()