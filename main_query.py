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

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from query_f.ocr_func import get_text_from_image_baidu
from query_f.win_func2 import analyze_current_screen_text
from query_f.win_func2 import get_area_data
from query_f.win_func2 import photo_capture
import configparser
import json

import requests

class question_answer:
   global data_directory,vm_name,app_name,search_engine,hot_key,ocr_engine,app_id,app_key,app_secret,api_version,hanwan_appcode,tz_value,token,header,url,textdir
   keyword = {} 
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
       self.textdir = conf.get('config',"textdir")
       
       if '冲顶大会' in self.app_name:
          self.token = conf.get('config',"cdtoken") 
          self.header = {
             'X-Live-Session-Token': self.token,
             'Content-Type': 'application/json',
          }       
          self.url = conf.get('config',"cdurl") 

#解析并搜索答案   
   def search_answer(self,keyword_r,type):
   
      elem = self.browser.find_element_by_id("kw")  
      for k,v in keyword_r.items():
   
         elem.clear()
         elem.send_keys(keyword_r['question'])
         elem.send_keys(' ')
         if type in k :
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
          self.keyword[k_p] = key_tmp
#          keyword_result[k_p] = key_tmp
   
#       return keyword_result
   def get_answer(self,answer_key):
      return answer_key.strip('[').strip(']').strip('"').strip('"').split('","')   

   def get_api_question(self):

       self.keyword = {}
       i = 0
#       print(self.url,self.header)
       while True:   
          resp = requests.get(self.url,headers=self.header)
          resultjson = json.loads(resp.text)
#          break
          if resultjson['msg'] == '成功' and resultjson['data']['type'] == 'showQuestion':
             print(resultjson)
 
             tmp_key = resultjson['data']['event']['options']
             self.keyword['question'] = resultjson['data']['event']['desc']
             answer_ar = self.get_answer(tmp_key)
             for i in range(len(answer_ar)):
                self.keyword['answer'+str(i+1)] = answer_ar[i]
             break
          else:
             print(resultjson)
#             print(resultjson['msg'])
#             print(resultjson['data']['type'])

             print("未获取到问题")
             i = i + 1
             if i == 120:
                break
             time.sleep(1)
             continue

   def copy_question(self):
       print("记录之前的问题")
       questiondir = os.path.join(self.textdir, 'question.txt')
       questiondirold = os.path.join(self.textdir, 'questionold.txt')

       if os.path.isfile(questiondir) :

          with open(questiondir, mode='r', encoding='utf-8') as f:
             quesfiletxt = f.readline()
          f.close()
          with open(questiondirold, mode='a+', encoding='utf-8') as f:
             f.writelines(quesfiletxt)
             f.writelines('\n')
          f.close()

   def log_question(self):
       questiondir = os.path.join(self.textdir, 'question.txt')
       questiondirold = os.path.join(self.textdir, 'questionold.txt')
       questionnew = ""
       questionnew = questionnew + self.keyword['question'] + '|'
       questionnew = questionnew + self.keyword['answer1'] + '|'
       questionnew = questionnew + self.keyword['answer2'] + '|'
       questionnew = questionnew + self.keyword['answer3'] + '|'
       
       with open(questiondir, mode='w+', encoding='utf-8') as f:
          f.writelines(questionnew)

   def read_photo(self):
       self.keyword={}
       print('我来识别这个题目是啥!!!')
       result_photo = analyze_current_screen_text(
           directory=self.data_directory,tz_value=self.tz_value
       )
#拆分问题和答案
       result_photo_q = []
       result_photo_a = []

       for k_p in result_photo :
          if 'question' in k_p :
             result_photo_q.append(k_p)
          elif 'answer' in k_p :
             result_photo_a.append(k_p)
#优先识别问题，并查询，再识别答案
       self.query_ocr(self.data_directory,result_photo_q)
       self.search_answer_2(self.keyword,'question',0)
       print(result_photo_a)
       self.query_ocr(self.data_directory,result_photo_a)
#       keyword_r = pre_process_question(keyword)
   
       if len(self.keyword) < 1:
           print("没识别出来，随机选吧!!!\n")
           print("题目出现的时候按F，我就自动帮你去搜啦~\n")
           return
       print("我用关键词:\" ", self.keyword, "\"去百度答案啦!")
   
#       print(keyword) 
#       self.search_answer(self.keyword)   

   def read_apiurl(self):
       self.keyword={}
       filekeyword = []
       print('通过api识别题目')
       print('当前APP为'+self.app_name)
       print('我来识别这个题目是啥!!!')

#将question中的题目记录到历史
       self.copy_question()
#调用api获得题目
       self.get_api_question()

#将读取到的问题记录到question.txt文件中
       if len(self.keyword) != 0:
          self.log_question()
#登录百度查询问题
          self.search_answer_2(self.keyword,'question',0)
       else:
          print('未获取到问题')

   def main(self):
#       self.read_photo()
       self.read_apiurl()
   
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

#只载入问题和答案
         if str(event) == 'f' or str(event) == 'F':
            self.main()

#载入问题和答案后搜索问题与答案的搜索量
         if str(event) == 'fd' or str(event) == 'FD':
            self.main()
            self.search_answer(self.keyword,'answer')
#载入问题和答案后搜索所有答案
         if str(event) == 'fa' or str(event) == 'FA':
            self.main()
            self.search_answer_2(self.keyword,'answer',0)
#载入问题和答案后搜索问题
         if str(event) == 'fs' or str(event) == 'FS':
            self.main()
            self.search_answer_2(self.keyword,'answer1',0)
#搜索问题与答案关联度                        
         if str(event) == 'd' or str(event) == 'D':
            self.search_answer(self.keyword,'answer')
#搜索答案
         if str(event) == 'a' or str(event) == 'A':
            self.search_answer_2(self.keyword,'answer',0)

            
         if str(event) == 'a1' or str(event) == 'A1':
            self.search_answer_2(self.keyword,'answer',1)
         if str(event) == 'a2' or str(event) == 'A2':
            self.search_answer_2(self.keyword,'answer',2)
         if str(event) == 'a3' or str(event) == 'A3':
            self.search_answer_2(self.keyword,'answer',3)
         if str(event) == 'a4' or str(event) == 'A4':
            self.search_answer_2(self.keyword,'answer',4)
#搜索问题

         if str(event) == 's' or str(event) == 'S':
            self.search_answer(self.keyword,'question',0)

#搜索问题与答案
         if str(event) == 's1' or str(event) == 'S1':
            self.search_answer(self.keyword,'1')
         if str(event) == 's2' or str(event) == 'S2':
            self.search_answer(self.keyword,'2')
         if str(event) == 's3' or str(event) == 'S3':
            self.search_answer(self.keyword,'3')
         if str(event) == 's4' or str(event) == 'S4':
            self.search_answer(self.keyword,'4')


      
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