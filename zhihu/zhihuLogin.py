#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
模拟登陆知乎
'''

import time
import re
import ConfigParser
import cookielib
import os.path
#安装模块
import requests
from bs4 import BeautifulSoup
from pprint import pprint

# 浏览器信息
agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
headers = {
    'Host': 'www.zhihu.com',
    'User-Agent': agent,
    'Accept': '*/*',
    'Referer': 'https://www.zhihu.com/',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.8'
}

# 读取配置文件
cf = ConfigParser.ConfigParser()
cf.read('config.ini')

session = requests.session()
session.cookies = cookielib.LWPCookieJar(filename='cookies.txt')

try:
    session.cookies.load(ignore_discard=True)
except:
    print('there is no cookie')

def get_xsrf():
    '''
    获取 xsrf 值
    '''
    response = requests.get('https://zhihu.com', headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    xsrf = soup.find('input',attrs={"name": "_xsrf"}).get('value')
    return xsrf

def get_captcha():
    '''
    1. 把验证码保存到当前目录，人工识别
    2. 第三方库pytesser 识别
    '''
    t = str(int(time.time() * 1000))
    captcha_url = 'https://zhihu.com/captcha.gif?r=' + t + '&type=login'
    r = session.get(captcha_url, headers=headers)
    with open('captcha.jpg','wb') as f:
        f.write(r.content)
        f.close()
    captcha = raw_input("input captcha: \n")
    return captcha

def isLog_in():
    url = 'https://www.zhihu.com/settings/profile'
    status = session.get(url, headers=headers, allow_redirects=False).status_code
    if(status==200):
        return True
    else:
        return False

def log_in(email, password):
    _xsrf = get_xsrf()
    headers["X-Xsrftoken"] = _xsrf
    headers["X-Requested-With"] = "XMLHttpRequest"
    login_url = 'https://zhihu.com/login/email'
    data = {
        '_xsrf': _xsrf,
        'password': password,
        'captcha': get_captcha(),
        'email': email
    }
    res = session.post(login_url, data=data, headers=headers)
    login_data = res.json()
    print(login_data['msg'])
    if login_data['r'] == 1:
        print('Login failed')
    else:
        for i in login_data:
            print(i)
    session.cookies.save()

if __name__ == '__main__':
    if isLog_in():
        print('you had login')
    else:
        email = cf.get('info', 'email')
        password = cf.get('info', 'password')
        log_in(email, password)

