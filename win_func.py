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


def analyze_current_screen_text(directory="."):
    """
    capture the VM screen now

    :return:
    """
    # print("capture time: ", datetime.now().strftime("%H:%M:%S"))
    screenshot_filename = "screenshot.png"
    tmp_file = "tmp.png"
    window_capture(0,tmp_file, directory)
    photo_capture(directory,tmp_file,screenshot_filename)
    save_text_area = os.path.join(directory, screenshot_filename)
    return get_area_data(save_text_area)






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