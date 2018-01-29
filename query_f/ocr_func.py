# -*- coding: utf-8 -*-

"""

    hanwan ocr service from aliyun

"""
import json

import base64
import requests
from aip import AipOcr

#测试功能
import configparser
import os


def get_text_from_image_baidu(image_data, app_id, app_key, app_secret, api_version=0, timeout=3):
    """
    Get image text use baidu ocr
    :param image_data:
    :param app_id:
    :param app_key:
    :param app_secret:
    :param api_version:
    :param timeout:
    :return:
    """
    client = AipOcr(appId=app_id, apiKey=app_key, secretKey=app_secret)
    client.setConnectionTimeoutInMillis(timeout * 1000)

    options = {}
    options["language_type"] = "CHN_ENG"

    if api_version == 1:
        result = client.basicAccurate(image_data, options)
    else:
        result = client.basicGeneral(image_data, options)

    if "error_code" in result:
        print("百度OCR识别出错，是不是免费使用次数用完了啊~")
        return ""
    return [words["words"] for words in result["words_result"]]


 
