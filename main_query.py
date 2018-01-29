#!/usr/bin/env python
# -*- coding:utf-8 -*-


"""

    问答助手~

"""
import sys
import os
import time
import win32gui
from argparse import ArgumentParser

import pyHook
import pythoncom
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from query_f.ocr_func import get_text_from_image_baidu
from query_f.win_func2 import analyze_current_screen_text
from query_f.win_func2 import get_area_data
from query_f.win_func2 import photo_capture
import configparser

class question_answer:
   global data_directory,vm_name,app_name,search_engine,hot_key,ocr_engine,app_id,app_key,app_secret,api_version,hanwan_appcode,tz_value
   keyword = None 
   browser = None
   
   
   def __init__(self):
       conf = configparser.ConfigParser()
       conf.read("config.ini")       
       self.data_directory = conf.get('config',"data_directory")   
       self.vm_name = conf.get('config',"vm_name")   
       self.app_name = conf.get('config',"app_name")   
       self.search_engine = conf.get('config',"search_engine")   
       self.hot_key = conf.get('config',"hot_key")
       self.ocr_engine = conf.get('config',"ocr_engine")
   
       ### baidu orc
       self.app_id = conf.get('config',"app_id")
       self.app_key = conf.get('config',"app_key")
       self.app_secret = conf.get('config',"app_secret")
   
       ### 0 表示普通识别
       ### 1 表示精确识别
       self.api_version = conf.get('config',"api_version")

#冲顶大会应为87  芝士超人为 0
       self.tz_value = conf.get('config',"tz_value")

#解析并搜索答案   
   def search_answer(self,keyword_r):
   
      elem = self.browser.find_element_by_id("kw")  
      for k,v in keyword_r.items():
   
         elem.clear()
         elem.send_keys(keyword_r['question.png'])
         elem.send_keys(' ')
         if 'answer' in k :
            elem.send_keys(keyword_r[k])
            elem.send_keys(Keys.RETURN)
            time.sleep(1)
            result = self.browser.find_element_by_class_name("nums")
            print('选项--------->' + keyword_r[k] + '<----------问题关联程度:')
            print(result.text)
   
   def search_answer_2(self,keyword_r,type,nu):
   
#      print(keyword_r)
   
      elem = self.browser.find_element_by_id("kw")
      elem.clear()

      for k,v in keyword_r.items():
      
         if type in k :
            if nu == 0 :
               elem.send_keys(keyword_r[k])
               elem.send_keys(' ')
            elif str(nu) in k:
               elem.send_keys(keyword_r[k])
               elem.send_keys(' ')
      
      elem.send_keys(Keys.RETURN)
   
#登录百度ocr识别图片   
   def query_ocr(self,directory,result_photo):
       keyword_result = {}
       for k_p in result_photo :
          save_text_area = os.path.join(directory, k_p)
          text_binary = get_area_data(save_text_area)
   
   #测试指定图片
   #    testfile = 'testjpg.png'
   #    testfile = 'test14.png'
   #    text_binary = get_area_data(os.path.join(data_directory,testfile)) 
   
          if self.ocr_engine == 'baidu':
              print("用百度去OCR识别--" + k_p + "--了!!!\n")
              keyword_q = get_text_from_image_baidu(image_data=text_binary, app_id=self.app_id, app_key=self.app_key,
                                                  app_secret=self.app_secret, api_version=self.api_version, timeout=5)       
          if not keyword_q:
              print("没识别出来，随机选吧!!!\n")
              print("题目出现的时候按F，我就自动帮你去搜啦~\n")
              return
          key_tmp = ""
          for k in keyword_q :
             key_tmp = key_tmp + k
          keyword_result[k_p] = key_tmp
   
       return keyword_result
   
   def main(self):
       print('我来识别这个题目是啥!!!')
   #    text_binary = analyze_current_screen_text(
   #        directory=data_directory
   #    )
   
       result_photo = analyze_current_screen_text(
           directory=self.data_directory,tz_value=self.tz_value
       )
   
       self.keyword = self.query_ocr(self.data_directory,result_photo)
   #    keyword_r = pre_process_question(keyword)
   
       if len(self.keyword) < 1:
           print("没识别出来，随机选吧!!!\n")
           print("题目出现的时候按F，我就自动帮你去搜啦~\n")
           return
       print("我用关键词:\" ", self.keyword, "\"去百度答案啦!")
   
#       print(keyword) 
#       self.search_answer(self.keyword)
   
   
       print("结果在浏览器里啦~\n")
       print("题目出现的时候按F，我就自动帮你去搜啦~\n")
   
   #测试百度ocr返回值
   def testocr(self):
       testfile = 'test14.png'
       text_binary = get_area_data(os.path.join(self.data_directory,testfile)) 
   
       if self.ocr_engine == 'baidu':
           print("用百度去OCR识别了!!!\n")
           keyword_to = get_text_from_image_baidu(image_data=text_binary, app_id=self.app_id, app_key=self.app_key,
                                               app_secret=self.app_secret, api_version=self.api_version, timeout=5)
       print(keyword)  
   
   def testcapture(self):
       testfile = 'testjpg.png'
       photo_capture(os.path.join(self.data_directory,testfile))
       image.getcolors()
       
   def moni(self):
      while True:
         event = input('输入f/F载入问题,输入d/D查询问题与答案关联度,输入a/A开始查询答案,输入s/S开始查询问题，输入q/Q退出程序')
         if str(event) == 'f' or str(event) == 'F':
            self.main()
         if str(event) == 'fd' or str(event) == 'FD':
            self.main()
            self.search_answer(self.keyword)

         if str(event) == 'd' or str(event) == 'D':
            self.search_answer(self.keyword)
            
         if str(event) == 'a' or str(event) == 'A':
            self.search_answer_2(self.keyword,'answer',0)
         if str(event) == 'fa' or str(event) == 'FA':
            self.main()

            self.search_answer_2(self.keyword,'answer',0)
         if str(event) == 'a1' or str(event) == 'A1':
            self.search_answer_2(self.keyword,'answer',1)
         if str(event) == 'a2' or str(event) == 'A2':
            self.search_answer_2(self.keyword,'answer',2)
         if str(event) == 'a3' or str(event) == 'A3':
            self.search_answer_2(self.keyword,'answer',3)
         if str(event) == 'a4' or str(event) == 'A4':
            self.search_answer_2(self.keyword,'answer',4)

         if str(event) == 's' or str(event) == 'S':
            self.search_answer_2(self.keyword,'question',0)

         if str(event) == 'fs' or str(event) == 'FS':
            self.main()
            self.search_answer_2(self.keyword,'question',0)
      
         if str(event) == 'q' or str(event) == 'Q':
            sys.exit()
         
         
         
         
#监控键盘消息钩子   
#def onKeyboardEvent(event):
#   
#   if str(event.Key) == 'f' or str(event.Key) == 'F':
#       print(str(event.Key))
##       qqq.main()
##      print(keyword)
##      testocr()
#   if str(event.Key) == 'a' or str(event.Key) == 'A':
#       search_answer_2(qqq.keyword,'answer')
#       print(qqq.keyword)
#   if str(event.Key) == 's' or str(event.Key) == 'S':
#       search_answer_2(qqq.keyword,'question')
#
#   if str(event.Key) == 'q' or str(event.Key) == 'Q':
#      sys.exit()
#   return True
   
   
if __name__ == "__main__":

    try:
        qa1 = question_answer()
#        init()
        print("配置文件正常加载!\n")
    except:
        print("配置文件异常，尝试使用默认配置\n")
    try:
        qa1.browser = webdriver.Chrome(r'.\tools\chromedriver.exe')
        qa1.browser.get(qa1.search_engine)

    except:
        print("chrome浏览器打开异常，可能是版本不对\n")
    
    print("题目出现的时候按F，我就自动帮你去搜啦~\n")
    print("按q退出程序\n")
#    hm = pyHook.HookManager()
#    hm.KeyDown = onKeyboardEvent
#    hm.HookKeyboard()
#    pythoncom.PumpMessages()
    qa1.moni()