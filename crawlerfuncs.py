"""
    该文件放置各网站不同的的爬取策略方法
    每个网站site的策略方法应成对编写 siteGetUrlset 与 siteGetArticle 两个方法
    之后按 'site': (siteGetUrlset, siteGetArticle) 放置在常量字典 FUNCS 中

    siteGetUrlSet( key, num=10) -> article_objects_list:
        :param str key: 搜索关键字，与停电内容相关
        :param int num: 指定结果最大收录的文章数量
        :return list article_objects_list: Article对象列表，须保证其url成员变量为非空且不重复
          即在本函数内，至少要定义返回的每个Article对象的 url字段

    siteGetArticle( article_object) -> article:
        :param object article_object: 一个Article对象
        :return object article: 一个Article对象
          在本函数内，至少要定义每个Article对象的 content/site/lang 字段

"""

import re
from urllib import request
import time
from time import sleep
import demjson
from Article import Article
from Key import Key
from datetime import date
from bs4 import BeautifulSoup as BF
import requests

from newspaper.api import fulltext
#------------------------------------------------------- Zhu ---------------------------------------------------------------


def cn2Utf8code( cn):
    return '%' + '%'.join(str(cn.encode('utf-8'))[4:-1].split(r'\x'))


def xinhuaCheckItem( item):
    """ xinhuaGetUrlSet子函数，用来检查json条目是否是需要的数据 """

    access_sitename = {
        '2014新版首页频道',
        '国际频道',
        '手机新华网2016',
        '应急救援频道'
    }

    if item[ 'sitename'] in access_sitename:
        return True

    return False


def xinhuaGetUrlSet(key, num=10):
    """
       新华网对关键字的搜索请求url为 http://so.news.cn/#search/0/KEY/PAGE/
       其中0表示第一优先级为文章（实测1是图片）；KEY为输入关键字；PAGE为结果分页，以1开始

       由此看来，新华网的搜索结果url集并不难拿到；但问题出自于，这个url集并不是一个完全干净的列表；
       其结果包括并不限于各种图片类文章、多媒体类文章、各应用版本重复文章（如同一篇文章同时出现在"手机新华网app"与正常页面中)

       所以针对这些多重的结果，爬虫优先考虑直接在本函数内过滤为格式大致统一的文章url集合。

    """
    if num > 20:
        raise KeyError( "Num should not be beyond 20")

    articles = list() # 放置结果

    urlends = list()  # 在新华网中，最后一级域名相同的url指向同一篇文章，需要过滤
    endpattern = re.compile(r'(\d+/)+(?P<urlend>.+)(?=\.htm)')  # 对每个url取出最后一级域名的re

    page = 1
    while len(urlends) < num:

        request_url = r'http://so.news.cn/getNews?' \
                      + 'keyword=' + cn2Utf8code(key) \
                      + '&curPage=' + str(page) \
                      + '&sortField=0' \
                      + '&searchFields=1&lang=cn'

        with request.urlopen(request_url) as json:

            json = demjson.decode(json.read(), encoding='utf8')

            # 无搜索结果， 返回空
            if json['content']['pageCount'] == 0:
                return None

            results = json['content']['results']

            for each_item in results:

                print('processing', each_item['url'], '...')

                if not xinhuaCheckItem(each_item): # 检查函数
                    print('checked: not pass')
                    continue

                each_item_urlend = endpattern.search( each_item['url']).group('urlend')
                if each_item_urlend in urlends: # 检查是否已收录
                    print('existed: not pass')
                    continue

                if len(urlends) > num:
                    print('records get boundary')
                    break  # 由于json是按页面迭代, 迭代过程中也要检查是否过量

                cur_article = Article()
                cur_article.url = each_item['url']
                cur_article.img = each_item['imgUrl']
                cur_article.pubtime = each_item['pubtime'][:10]

                articles.append(cur_article)
                urlends.append(each_item_urlend)

                print(each_item['url'], '---', each_item['sitename'], 'saved')

            page += 1
            if (page > json['content']['pageCount']): break  # 超过最大页数

            sleep(2)

    return articles

#-------------------------------------------------------end Zhu ------------------------------------------------------------



#------------------------------------------------------- Xu ----------------------------------------------------------------

def baiduGetUrlSet(self, key_word) -> set:

    container_list = []  # 存放临时URL
    articles = list()  # article 集合
    baidu_url_list = ["https://www.baidu.com/s?ie=UTF-8&wd=" + key_word,
                      "https://www.baidu.com/s?ie=UTF-8&tn=news&wd=" + key_word]
    #百度网页搜索与新闻搜索
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
            #多个页面
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
                    cur_article = Article()
                    cur_article.url = real_url + '\n'
                    try:
                        cur_article.img = container.find("img", {"class": "c-img c-img6"}).get("src")
                        #有些搜索结果没有图片
                    except:
                        cur_article.img = ""
                    cur_article.pubtime = container.find("span", {"class": " newTimeFactor_before_abs m"}).get_text()[:-13]
                    raw_title = container.find("h3", {"class": "t"}).find("a").get_text()
                    cur_article.title = re.sub("\"|<em>|</em>", "", raw_title)
                    articles.append(cur_article)
                container_list = []
        else:
            for container in container_list:
                href = container.find("h3").find("a").get("href")
                if "baijiahao" in href:
                    continue
                else:
                    cur_article = Article()
                    cur_article.url = real_url + '\n'
                    cur_article.img= ""
                    cur_article.pubtime = container.find("span", {"class": " newTimeFactor_before_abs m"}).get_text()[
                                          :-17]
                    raw_title = container.find("h3", {"class": "c-title"}).find("a").get_text()
                    cur_article.title = re.sub("\"|<em>|</em>", "", raw_title)
                    articles.append(cur_article)
    return articles


def googleGetUrlSet(self, key_word) -> set:
    google_url_list = ["https://www.google.com.hk/search?q=" + key_word,
                       "https://www.google.com/search?q={}&tbm=nws".format(key_word)]
    container_list = []  # 存放临时URL
    articles = list()  # article 集合
    for google_tag in range(0,2):
        try:
            self.driver.get(google_url_list[google_tag])
        except:
            self.driver.refresh()
        # 需要刷新一下界面
        time.sleep(2)
        self.driver.refresh()
        time.sleep(5)
        self.driver.get(google_url_list[google_tag])
        for page in range(1, self.MAX_PAGEs + 1):
            BF1 = BF(self.driver.page_source)
            # print(driver.page_source)
            page_container_list = BF1.findAll("div", {"class": "g"})
            for container in page_container_list:
                try:
                    if google_tag == 0:
                        imge_url = ""
                        title = container.find("h3").get_text()
                        pubtime = container.find("span", {"class": "f"}).get_text()
                    else:
                        try:
                            imge_url = container.find("img").get("src")
                        except
                            imge_url = ""
                        raw_title = container.find("h3").find("a").get_text()
                        title = re.sub("\"|<em>|</em>", "", raw_title)
                        pubtime = container.find("span", {"class": "f nsa fwzPFf"}).get_text()
                    href = container.find("a").get("href")
                except:
                    continue
                cur_article = Article()
                cur_article.title = title
                cur_article.img = imge_url
                cur_article.url = href
                cur_article.pubtime = pubtime
                articles.append(cur_article)

            b = self.driver.find_element_by_xpath("//*[text()='下一页']").click()
            time.sleep(2)
    return articles

def wikiGeturlSet(self, key_word) -> list():
    wiki_url="https://zh.wikipedia.org/w/index.php?sort=relevance&profile=advanced&fulltext=1&ns0=1&search"+key_word
    articles = list()  # URL集
    self.driver.get(wiki_url)
    bf1 = BF(self.driver.page_source, 'lxml')
    container_list = bf1.findALL("li", {"class": "mw-search-result"})
    for container in container_list:
        try:
            imge_url = ""
            href = "https://zh.wikipedia.org/"+container.find("a").get("href")
            title = container.find("a").get_text()
            raw_pubtime = container.find("div", {"class": "mw-search-result-data"}).get_text()
            pattern = re.compile(".*- (.*)")
            pubtime = re.match(pattern, pubtime).group(1)
        except:
            continue
        cur_article = Article()
        cur_article.title = title
        cur_article.img = imge_url
        cur_article.url = href
        cur_article.pubtime = pubtime
        articles.append(cur_article)
    return articles

def cnnGetUrlSet(self, key_word) -> set:
    container_list = []  # 存放临时URL
    articles = list()  # URL集

    cnn_url = "https://edition.cnn.com/search?size=20&q="+key_word
    self.driver.get(cnn_url)
    bf1 = BF(self.driver.page_source, 'lxml')
    container_list = bf1.findALL("div", {"class": "cnn-search__result cnn-search__result--article"})

    for container in container_list:
        try:
            imge_url = container.find("div", {"class": "cnn-search__result-thumbnail"}).find("img").get("src")
            href = container.find("div", {"class": "cnn-search__result-contents"}).find("h3").find("a").get("href")
            title = container.find("div", {"class": "cnn-search__result-contents"}).find("h3").find("a").get_text()
            pubtime = container.find("div", {"class": "cnn-search__result-publish-date"}).findAll("span")[1].get_text()
        except:
            continue
        cur_article = Article()
        cur_article.title = title
        cur_article.img = imge_url
        cur_article.url = href
        cur_article.pubtime = pubtime
        articles.append(cur_article)
    return articles


def abcNewsGetUrlSet(self, key_word) -> set:
    container_list = []  # 存放临时URL
    articles = list()  # URL集

    # abcNews

    abcNews_url = "https://abcnews.go.com/search?r=week&searchtext="+key_word
    self.driver.get(abcNews_url)
    BF1 = BF(self.driver.page_source, 'lxml')
    container_list = BF1.findALL("div", {"class": re.compile("result.*")})

    for container in container_list:
        # try:
        #     href = container.find("a", {"class": "title"}).get("href")
        #     title = container.find("a", {"class": "title"}).get_text()
        # except:
        #     continue
        try:
            imge_url = container.find("div", {"class": "cnn-search__result-thumbnail"}).find("img").get("src")
            href = container.find("div", {"class": "cnn-search__result-contents"}).find("h3").find("a").get("href")
            title = container.find("div", {"class": "cnn-search__result-contents"}).find("h3").find("a").get_text()
            pubtime = container.find("div", {"class": "cnn-search__result-publish-date"}).findAll("span")[1].get_text()
        except:
            continue
        cur_article = Article()
        cur_article.title = title
        cur_article.img = imge_url
        cur_article.url = href
        cur_article.pubtime = pubtime
        articles.append(cur_article)
    return articles


def tassGetUrlSet(self, key_word) -> list:
    container_list = []  # 存放临时URL
    articles = list()  # URL集

    # tass

    tass_url = "https://tass.com/search?sort=date&range=week&searchStr" + key_word
    self.driver.get(tass_url)
    BF1 = BF(self.driver.page_source, 'lxml')
    container_list = BF1.findALL("div", {"class": "news-list__item ng-scope"})

    for container in container_list:
        try:
            href = "www.tass.con/" + container.find("a").get("href")
            title = container.find("span", {"class": "news-preview__title ng-binding"}).get_text()
            try:
                imge_url = container.find("div", {"data-ng-if": "item.image"}).find("div").get("style")[23:-2]
            except:
                imge_url = ""
            self.driver.get(href)
            BF1 = BF(self.driver.page_source, 'lxml')
            pubtime = BF1.find("span", {"data-ng-if": "visibleDate"}).get_text()
        except:
            continue
        cur_article = Article()
        cur_article.title = title
        cur_article.img = imge_url
        cur_article.url = href
        cur_article.pubtime = pubtime
        articles.append(cur_article)
    return articles


def baiduGetArticle(url) -> dict:
    article = dict()
    # do some thing
    return article

def getArticle(self, key_word, articles):

    count = 0
    for article in articles:
        try:
            time.sleep(1)
            try:
                self.driver.get(article.url)
            except:
                self.driver.refresh()
            time.sleep(2)
            self.driver.refresh()
            js = "var q=document.documentElement.scrollTop=100000"
            self.driver.execute_script(js)
            time.sleep(3)
            text = fulltext(self.driver.page_source, language='zh')
            # news=Article(real_url,language='zh')
            # news.download()
            # news.parse()
            article.content = text

            # filename = str(count) + ".txt"
            # f = open(path + "/" + filename, "w")
            # # f.write(news.title)
            # f.write(real_url)
            # # f.write(news.text)
            # print(text)
            # f.write(text)
            # f.close()
            count = count + 1
        except:
            continue
    return 0


def getKeys(key_content) -> list:
    key_list = key_content.split(";")
    real_key_list= list()
    for key in key_list:
        if not key == "":
            continue
        p = re.compile('[a-z ]+')
        cur_Key = Key()
        if p.match(key[0]):
            cur_Key.language=1
        else:
            cur_Key.language=0
        cur_Key.key=key
    return real_key_list
#-------------------------------------------------------end Xu --------------------------------------------------------------

FUNCS = {

}

def test():

    # s = xinhuaGetUrlSet('停电', num=20)
    #
    # for each_article in s:
    #     print('{:40} {}'.format(each_article.url, each_article.pubtime))

    t = tassGetUrlSet("blackout")




test()