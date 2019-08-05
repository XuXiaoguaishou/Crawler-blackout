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
from time import sleep
import demjson
from Article import Article
from datetime import date
from bs4 import BeautifulSoup as BF
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
def baiduGetUrlSet(key, num=10) -> set:
    urlset = set()
    # do some thing
    return urlset


def baiduGetArticle(url) -> dict:
    article = dict()
    # do some thing
    return article

def cnnGetUrlSet(self, key_word) -> set:
    container_list = []  # 存放临时URL
    real_url_set = set()  # URL集

    # CNN

    cnn_url = "https://edition.cnn.com/search?size=20&q="+key_word
    self.driver.get(cnn_url)
    bf1 = BF(self.driver.page_source, 'lxml')
    container_list=bf1.findALL("div", {"class": "cnn-search__result-contents"})

    for container in container_list:
        try:
            href = container.find("h3").find("a").get("href")
            title = container.find("h3").find("a").get_text()
        except:
            continue
        real_url_set.add((href, title))

    return real_url_set


def abcNewsGetUrlSet(self, key_word) -> set:
    container_list = []  # 存放临时URL
    real_url_set = set()  # URL集

    # abcNews

    abcNews_url = "https://abcnews.go.com/search?r=week&searchtext="+key_word
    self.driver.get(abcNews_url)
    BF1 = BF(self.driver.page_source, 'lxml')
    container_list = BF1.findALL("div", {"class": re.compile("result.*")})

    for container in container_list:
        try:
            href = container.find("a", {"class": "title"}).get("href")
            title = container.find("a", {"class": "title"}).get_text()
        except:
            continue
        real_url_set.add((href, title))

    return real_url_set


def tassGetUrlSet(self, key_word) -> set:
    container_list = []  # 存放临时URL
    real_url_set = set()  # URL集

    # tass

    tass_url = "https://tass.com/search?sort=date&searchStr" + key_word
    self.driver.get(tass_url)
    BF1 = BF(self.driver.page_source, 'lxml')
    container_list = BF1.findALL("div", {"class": "news-list__item ng-scope"})

    for container in container_list:
        try:
            href = "www.tass.con/" + container.find("a").get("href")
            title = container.find("span", {"class": "news-preview__title ng-binding"}).get_text()
        except:
            continue
        real_url_set.add((href, title))

    return real_url_set


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