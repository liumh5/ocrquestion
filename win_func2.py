#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

    capture the VM screen
    then use hanwang text recognize the text
    then use baidu to search answer

"""

import ctypes
import os
import time
import win32gui

import win32com.client
import win32con
from PIL import Image, ImageGrab
import win32ui
import win32api
import cv2
import numpy as np



class box:
   x = 0
   y = 0
   height = 0
   width = 0   
   def __init__(self,tmp_box):
      #计算坐标并截图
      Xs = [i[0] for i in tmp_box]
      Ys = [i[1] for i in tmp_box]
      x1 = min(Xs)
      x2 = max(Xs)
      y1 = min(Ys)
      y2 = max(Ys)
      self.hight = y2 - y1
      self.width = x2 - x1
      self.x = x1
      self.y = y1
   def bbOverlap(self,box2):
   
     if (self.x > box2.x+box2.width):
        return False
     if (self.y > box2.y+box2.hight):
        return False
     if (self.x+self.width < box2.x):
        return False
     if (self.y+self.hight < box2.y):
        return False
     colInt =  min(self.x+self.width,box2.x+box2.width) - max(self.x, box2.x)
     rowInt =  min(self.y+self.hight,box2.y+box2.hight) - max(self.y,box2.y)
     intersection = colInt * rowInt
     area1 = self.width*self.hight
     area2 = box2.width*box2.hight
     if intersection / (area1 + area2 - intersection) != 0 :
        return True
     else:
        return False
        
        
        
def analyze_current_screen_text(directory=".",tz_value=0):
    """
    capture the VM screen now

    :return:
    """
    # print("capture time: ", datetime.now().strftime("%H:%M:%S"))
    screenshot_filename = "screenshot.png"
    tmp_file = "first_tmp.png"
    window_capture(0,tmp_file, directory)
#    photo_capture(directory,tmp_file,screenshot_filename)
    print(tz_value)
    result = get_box(directory,tmp_file,np.int0(tz_value))

#    save_text_area = os.path.join(directory, screenshot_filename)
#    return get_area_data(save_text_area)
    return result





def window_capture(hwnd,filename,directory):
#   directory = 'd:'
    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()
    saveBitMap = win32ui.CreateBitmap()
#   MoniterDev = win32api.EnumDisplayMonitors(None,None)
#   w = MoniterDev[0][2][2]
#   h = MoniterDev[0][2][3]
    w = 600
    h = 650
    saveBitMap.CreateCompatibleBitmap(mfcDC,w,h)
    saveDC.SelectObject(saveBitMap)
#   saveDC.BitBlt((0,0),(w,h),mfcDC,(0,0),win32con.SRCCOPY)
    saveDC.BitBlt((0,0),(w,h),mfcDC,(1300,0),win32con.SRCCOPY)
    saveBitMap.SaveBitmapFile(saveDC,os.path.join(directory, filename))
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)


def get_photo(img,box,pyvalue):
#计算坐标并截图
   Xs = [i[0] for i in box]
   Ys = [i[1] for i in box]
   x1 = min(Xs)
   x2 = max(Xs)
   y1 = min(Ys)
   y2 = max(Ys)
   hight = y2 - y1
   width = x2 - x1
   #cropimg = img[y1:y1+hight, x1:x1+width]
#y1+pyvalue  图片上限下移   y1+hight-20 图片下限上移
#   cropimg = img[y1+pyvalue:y1+hight-20, x1:x1+width]
   cropimg = img[y1+pyvalue:y1+hight, x1:x1+width]
   return cropimg

def box_if_overlap(baa):
   dlist = []
   baa_r = []
   for i in range(len(baa)):
      box1 = box(baa[i])
      for j in range(len(baa)):
         if i != j :
            box2 = box(baa[j])
            if box1.bbOverlap(box2):
#               print(i,j,cv2.contourArea(baa[i]),cv2.contourArea(baa[j]))
               if cv2.contourArea(baa[i]) < cv2.contourArea(baa[j]):
                  dlist.append(i)
               else:
                  dlist.append(j)
   for i in range(len(baa)):
      if i not in dlist :
         baa_r.append(baa[i])
   return baa_r

def calu_box_all(cba,cba_min,cbavalue):
   cba_r = []
   Xs = [i[0] for i in cba]
   Ys = [i[1] for i in cba]
   x1 = min(Xs)
   x2 = max(Xs)
   y1 = min(Ys)
   y2 = max(Ys)

   for k in cba:
      if k[1] == y2:
         k[1] = cba_min
      if k[1] == y1:
         k[1] = k[1] + cbavalue
   cba_r.append(cba)
   return cba_r

def get_box(directory,file,ppvalue):
   jpgfile = os.path.join(directory, file)   
   img = cv2.imread(jpgfile)
   gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
   ret, binary = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY)
   binary,contours,hierarchy = cv2.findContours(binary,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
   cnt_all_array = []
   cnt_answer_array = []
   for i in range(len(contours)):
      cnt = contours[i]
      area = cv2.contourArea(cnt)
      if area > 100000:    
         cnt_all_array.append(cnt)
   for i in range(len(contours)):
      cnt = contours[i]
      area = cv2.contourArea(cnt)
      if area > 20000 and area < 40000:
#         print(cv2.contourArea(cnt))
         cnt_answer_array.append(cnt)


   rect_all_array = []
   rect_answer_array = []
   box_all_array = []
   box_answer_array = []
   for k in cnt_all_array :
      rect_all_array.append(cv2.minAreaRect(k))
   for k in cnt_answer_array :
      rect_answer_array.append(cv2.minAreaRect(k))
   for k in rect_all_array :
      box_all_array.append(np.int0(cv2.boxPoints(k)))
   for k in rect_answer_array :
      box_answer_array.append(np.int0(cv2.boxPoints(k)))      

   box_answer_array = box_if_overlap(box_answer_array)
   
   min=100000
   for k1 in box_answer_array :
      for k2 in k1 :
         if min > k2[1]:
            min = k2[1]
#   print(min)
#   print(box_all_array[0])
#   print(ppvalue)
   
   box_all_array = calu_box_all(box_all_array[0],min,ppvalue)
#   box_all_array[0][0][1]=min
#   box_all_array[0][3][1]=min
#   box_all_array[0][1][1]=box_all_array[0][1][1] + ppvalue
#   box_all_array[0][2][1]=box_all_array[0][2][1] + ppvalue
   
#   print(box_all_array[0])
#   print(box_all_array[0])
   result = []   
   result_file = 'question.png'
   cpimg = get_photo(img,box_all_array[0],0)
   cv2.imwrite(os.path.join(directory, result_file), cpimg)      
   result.append(result_file)
   for i in range(len(box_answer_array)):
      result_file = 'answer'+str(len(box_answer_array)-i)+'.png'
      result.append(result_file)
      cpimg = get_photo(img,box_answer_array[i],0)
      cv2.imwrite(os.path.join(directory, result_file), cpimg)
   return result

def photo_capture(directory,file,result_file):
   
   jpgfile = os.path.join(directory, file)
    
   img = cv2.imread(jpgfile)
   gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
   ret, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
   binary,contours,hierarchy = cv2.findContours(binary,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
   for i in range(len(contours)):
      cnt = contours[i]
      area = cv2.contourArea(cnt)
      if area > 200000:    
         break
   rect = cv2.minAreaRect(cnt)
   box=cv2.boxPoints(rect)
   box = np.int0(box)
   cpimg = get_photo(img,box,90)
   cv2.imwrite(os.path.join(directory, result_file), cpimg)


def get_area_data(text_area_file):
    """

    :param text_area_file:
    :return:
    """
    with open(text_area_file, "rb") as fp:
        image_data = fp.read()
        return image_data
    return ""
    
if __name__ == "__main__":
   data_directory='screenshots'
#   analyze_current_screen_text(directory=data_directory)
#   photo_capture()