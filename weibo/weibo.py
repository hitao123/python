#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
 爬取微博用户图片
'''
import re
import string
import sys
import os
import urllib
import urllib2
import requests
import cookielib
from bs4 import BeautifulSoup
from lxml import etree

#改变默认字符集，windows下为 ascii
reload(sys) 
sys.setdefaultencoding('utf-8')

if(len(sys.argv) >= 2):
    user_id = (int)(sys.argv[1])
else:
    user_id = (int)(raw_input("input user_id: \n"))

# 浏览器信息
agent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1'
headers = {
    'Host': 'm.weibo.cn',
    'User-Agent': agent,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8'
}

#类似 C语言 printf('%d',a)
url = 'http://weibo.cn/u/%d?filter=1&page=1'%user_id

#获取 session
# response = requests.get(url, headers=headers)

# session = requests.session()
# session.cookies = cookielib.LWPCookieJar(filename='cookies.txt')
# try:
#     session.cookies.load(ignore_discard=True)
# except:
#     print('there is no cookie')

cookie = {"Cookie": "_T_WM=b8c2ef1a7e862beb1e5e23a8231e30cd; ALF=1496625089; SCF=Aggf9Cs_2MQpRlGyzSc4of4fS0Vd5JyOXoxztEyI26D3-h-j7Lh92yuW5ZultkT8R6axqqkTcX3ilVSbZtU5xSc.; SUB=_2A250CVNKDeThGeNO4lQT9SvJwzWIHXVX8n0CrDV6PUJbktANLXfjkW0VNlsVbVhPXeKu-uJvkAKp3V3uUg..; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFM1MTs3wiLsFSzPx9VuGp65JpX5o2p5NHD95Qfeh.ceo-fSKn4Ws4DqcjGIHxyd0zEe5tt; SUHB=0FQ7P6S31kHAgw; SSOLoginState=1494033178; M_WEIBOCN_PARAMS=featurecode%3D20000320%26luicode%3D10000011%26lfid%3D2302831757353251%26fid%3D1005051757353251%26uicode%3D10000011"}


html = requests.get(url, cookies=cookie).content

#将html写进去
with open("index.xml", "wb") as code:
    code.write(html)
    code.close()

selector = etree.HTML(html)
#获取总页数
pageNum = (int)(selector.xpath('//input[@name="mp"]')[0].attrib['value'])

#拼接字符串
result = ""
#无序不重复元素集，这里存储图片url
urllist_set = set()
#文字数
word_count = 1
#图片数
image_count = 1

print u'爬虫准备就绪...'


for page in range(1, 20):

    #获取lxml页面
    url = 'http://weibo.cn/u/%d?filter=1&page=%d'% (user_id, page) 
    html2 = requests.get(url, cookies=cookie).content

    #title爬取
    selector = etree.HTML(html2)
content = selector.xpath('//span[@class="ctt"]')
for each in content:
    text = each.xpath('string(.)')
    if word_count >= 4:
        text = "%d : "%(word_count-3) + text + "\n\n"
    else:
        text = text + "\n\n"
    result = result + text
    word_count += 1

#图片爬取
soup = BeautifulSoup(html, "lxml")
urllist = soup.find_all('a', href=re.compile(r'^https://weibo.cn/mblog/pic/',re.I))

for imgurl in urllist:
    urllist_set.add(imgurl.img['src'])
    image_count += 1

with open("%s"%user_id + ".txt", "wb") as fo:
    fo.write(result)
    fo.close()
word_path = os.getcwd()
print u'文字微博爬取完毕'

link = ""
with open("img.txt", "wb") as fo2:
    for eachlink in urllist_set:
        link = link + eachlink + "\n"
    fo2.write(link)
    fo2.close()
# fo2 = open("/image/%s_imageurls"%user_id, "wb")
# for eachlink in urllist_set:
#   link = link + eachlink +"\n"
# fo2.write(link)
# fo2.close()
print u'图片链接爬取完毕'

if not urllist_set:
    print u'该页面中不存在图片'
else:
    #下载图片,保存在当前目录的weibo_image文件夹下
    image_path = os.getcwd() + '/weibo_image'
    if os.path.exists(image_path) is False:
        os.mkdir(image_path)
    x = 1
    for imgurl in urllist_set:
        temp = image_path + '/%s.jpg' % x
        print u'正在下载第%s张图片' % x
        try:
            urllib.urlretrieve(urllib2.urlopen(imgurl).geturl(),temp)
        except:
            print u"该图片下载失败:%s"% imgurl
        x += 1

print u'原创微博爬取完毕，共%d条，保存路径%s'%(word_count-4,word_path)
print u'微博图片爬取完毕，共%d张，保存路径%s'%(image_count-1,image_path)