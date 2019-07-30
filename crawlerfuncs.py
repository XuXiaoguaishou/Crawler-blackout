"""
    该文件放置各网站不同的的爬取策略方法
    每个网站site的策略方法应成对编写 siteGetUrlset 与 siteGetArticle 两个方法
    之后按 'site': (siteGetUrlset, siteGetArticle) 放置在常量字典 FUNCS 中

    siteGetUrlSet( key, num=10) -> urlset:
        :param str key: 搜索关键字，与停电内容相关
        :param int num: 指定结果最大收录的文章数量
        :return set urlset: （url, title）该站对key搜索的(结果链接,标题)集合, 其长度 <= num(当所有文章无重时取等于)

    siteGetArticle( url ) -> article:
        :param str url: 文章url
        :return str article: 一个字典。其中包含了这篇文章的以下信息：
            article{
                'content':  str 文章内容，
                'site':     str 来源站点，
                'image':    str 一张代表图片的url
            }
"""
from bs4 import BeautifulSoup as BF
import re
import selenium
#------------------------------------------------------- Zhu ---------------------------------------------------------------


pass

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
    'baidu': (baiduGetUrlSet, baiduGetArticle)
}
