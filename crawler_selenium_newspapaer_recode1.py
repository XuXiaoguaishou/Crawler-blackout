# -*- coding: utf-8 -*-
from selenium import webdriver
import requests
from bs4 import BeautifulSoup as BF
import re

from newspaper import Article
from newspaper.api import fulltext
import time
import os

import multiprocessing


def get_url_set(self, key_word):
    container_list = []  # 存放临时URL
    real_url_set = set()  # URL集

    # CNN

    CNN_url = "https://edition.cnn.com/search?size=20&q="+key_word
    self.driver.get(CNN_url)
    BF1 = BF(self.driver.page_source, 'lxml')
    container_list=BF1.findALL("div", {"class", "cnn-search__result-contents"})

    for container in container_list:
        try:
            href=container.find("h3").find("a").get("href")
        except:
            continue
        real_url_set.add(container)

    def get_url_set(self, key_word):
        container_list = []  # 存放临时URL
        real_url_set = set()  # URL集

        # CNN

        CNN_url = "https://edition.cnn.com/search?size=20&q=" + key_word
        self.driver.get(CNN_url)
        BF1 = BF(self.driver.page_source, 'lxml')
        container_list = BF1.findALL("div", {"class", "cnn-search__result-contents"})

        for container in container_list:
            try:
                href = container.find("h3").find("a").get("href")
            except:
                continue
            real_url_set.add(container)



    for i in range(2):
        self.driver.get(baidu_url_list[i])
        # 获取每条搜索结果的URL
        for page in range(1, self.MAX_PAGEs + 1):
            BF1 = BF(self.driver.page_source, 'lxml')
            # print(driver.page_source)
            if i == 0:
                page_container_list = BF1.findAll("div", {"class": re.compile(".*c-container.*")})
            else:
                page_container_list = BF1.findAll("div", {"class": re.compile("result")})
            # print(page_container_list)
            container_list.extend(page_container_list)
            b = self.driver.find_element_by_xpath("//*[text()='下一页>']").click()
            time.sleep(2)
        if i == 0:
            # print(container_list)
            for container in container_list:
                # print(container)
                try:
                    href = container.find("h3").find("a").get("href")
                    baidu_url = requests.get(url=href, headers=self.headers, allow_redirects=False)
                except:
                    continue
                real_url = baidu_url.headers['Location']  # 得到网页原始地址
                if real_url.startswith('http'):
                    real_url_set.add(real_url + '\n')
                container_list = []
        else:
            for container in container_list:
                href = container.find("h3").find("a").get("href")
                if "baijiahao" not in href:
                    real_url_set.add(href)




class crawler:
    driver=None
    key_list=[]
    MAX_PAGEs = 2
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, compress',
        'Accept-Language': 'en-us;q=0.5,en;q=0.3',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'
    }
    method="selenium_newspaper"

    def __init__(self, key_list):
        self.key_list=key_list
        options = webdriver.ChromeOptions()
        prefs={
            'profile.default_content_setting_values': {
                'images': 2,
                #'video':2
            }
        }
        #options.add_argument("--user-data-dir="+r"C:/Users/Liuyus\AppData/Local/Google/Chrome/User Data/")
        options.add_experimental_option('prefs',prefs)
        self.driver = webdriver.Chrome(executable_path=r"H:\Github\Blackout-Crawler\mysite\crawler\chromedriver.exe",chrome_options=options)

    
    def get_url_set(self,key_word):
        container_list=[]           #存放临时URL
        real_url_set=set()          #URL集
        
        #百度网页搜索+百度资讯搜索结果

        baidu_url_list=["https://www.baidu.com/s?ie=UTF-8&wd="+key_word,"https://www.baidu.com/s?ie=UTF-8&tn=news&wd="+key_word]
        for i in range(2):
            self.driver.get(baidu_url_list[i])
            #获取每条搜索结果的URL
            for page in range(1,self.MAX_PAGEs+1):
                BF1=BF(self.driver.page_source,'lxml')
                #print(driver.page_source)
                if i==0:
                    page_container_list=BF1.findAll("div",{"class":re.compile(".*c-container.*")})
                else:
                    page_container_list=BF1.findAll("div",{"class":re.compile("result")})
                #print(page_container_list)
                container_list.extend(page_container_list)
                b=self.driver.find_element_by_xpath("//*[text()='下一页>']").click()
                time.sleep(2)
            if i==0:
                #print(container_list)
                for container in container_list:
                    #print(container)
                    try:
                        href = container.find("h3").find("a").get("href")
                        baidu_url = requests.get(url=href, headers=self.headers, allow_redirects=False)
                    except:
                        continue
                    real_url = baidu_url.headers['Location']  #得到网页原始地址
                    if real_url.startswith('http'):
                        real_url_set.add(real_url + '\n')
                    container_list=[]
            else:
                for container in container_list:
                    href=container.find("h3").find("a").get("href")
                    if "baijiahao" not in href:
                        real_url_set.add(href)


        #必应搜索结果
        
        being_url="https://cn.bing.com/search?q="+key_word+"&FORM=PORE"
        try:
            self.driver.get(being_url)
        except:
            self.driver.refresh()
        #需要刷新一下界面
        time.sleep(2)
        self.driver.refresh()
        time.sleep(5)
        for page in range(1,self.MAX_PAGEs+1):
            BF1=BF(self.driver.page_source)
            #print(driver.page_source)
            page_container_list=BF1.find("ol",{"id":"b_results"}).findAll("h2")
            for page_container in page_container_list:
                try:
                    real_url_set.add(page_container.find("a").get('href'))
                except:
                    break
            try:
                b=self.driver.find_element_by_xpath(".//*[@title='下一页']").click()
            except:
                b=self.driver.find_element_by_xpath(".//*[@title='Next page']").click()
            time.sleep(2)
        #谷歌网页加谷歌新闻  #需使用VPN
        google_url_list=["https://www.google.com.hk/search?q="+key_word,"https://www.google.com/search?q={}&tbm=nws".format(key_word)]
        for google_url in google_url_list:    
            try:
                self.driver.get(google_url)
            except:
                self.driver.refresh()
            #需要刷新一下界面
            time.sleep(2)
            self.driver.refresh()
            time.sleep(5)
            self.driver.get(google_url)
            for page in range(1,self.MAX_PAGEs+1):
                BF1=BF(self.driver.page_source)
                #print(driver.page_source)
                page_container_list=BF1.findAll("div",{"class":"g"})
                for page_container in page_container_list:
                    try:
                        real_url_set.add(page_container.find("a").get('href'))
                    except:
                        break
                b=self.driver.find_element_by_xpath("//*[text()='下一页']").click()
                time.sleep(2)

        #Wikipedia 需使用VPN
        Wikipedia_url="https://zh.wikipedia.org/w/index.php?search="+key_word+"&limit=100&ns0=1"
        self.driver.get(Wikipedia_url)
        BF1=BF(self.driver.page_source)
        page_container_list=BF1.findAll("div",{"class":"mw-search-result-heading"})
        for page_container in page_container_list:
            try:
                real_url_set.add("https://zh.wikipedia.org"+page_container.find("a").get('href'))

            except:
                break

        print(*real_url_set)
        print('-----------------------------')
        print(*self.key_list)
        return real_url_set

    def getArticle(self,key_word,real_url_set):
        path="C:/Users/Liuyus/Desktop/大停电爬虫/"+self.method+key_word
        os.mkdir(path)
        print(real_url_set)
        count=0
        for real_url in real_url_set:
            try:
                time.sleep(1)
                try:
                    self.driver.get(real_url)
                except:
                    self.driver.refresh()
                time.sleep(2)
                self.driver.refresh()
                
                js="var q=document.documentElement.scrollTop=100000"  
                self.driver.execute_script(js)
                time.sleep(3)
                text=fulltext(self.driver.page_source,language='zh')
                #news=Article(real_url,language='zh')
                #news.download()
                #news.parse()
                print(real_url)
                print(self.driver.page_source)
                filename=str(count)+".txt"
                f=open(path+"/"+filename,"w")
                #f.write(news.title)
                f.write(real_url)
                #f.write(news.text)
                print(text)
                f.write(text)
                f.close()
                count=count+1
            except:
                continue
        return 0

    def begin(self):
        real_url_sets=[]
        for key_word in self.key_list:
            real_url_set = self.get_url_set(key_word)
            real_url_sets.append(real_url_set)
            print(real_url_set)
            self.getArticle(key_word, real_url_set)
            print(len(real_url_set))
        return real_url_sets

a=crawler(['shafa','aqwer'])
l = a.begin()
print(*l)
#a.get_url_set('fs')

