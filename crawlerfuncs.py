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
from selenium import webdriver
import re
from urllib import request
import time
from time import sleep
import demjson
from Article import Article
#from Key import Key
from datetime import date
from bs4 import BeautifulSoup as BF
import requests

from newspaper.api import fulltext
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities



MAX_PAGE = 1
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, compress',
    'Accept-Language': 'en-us;q=0.5,en;q=0.3',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'
}
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

def reutersGetUrlSet(key_word) ->list:
    driver = get_driver(0,0)
    articles = []  # URL集
    reuters_url = "https://cn.reutersmedia.net/assets/searchArticleLoadMoreJson?" + \
          "blob=" + key_word + "&" + \
          "bigOrSmall=big&articleWithBlog=true&sortBy=relevance&" + \
          "dateRange=all&numResultsToShow=20" +\
          "&pn=1&callback=addMoreNewsResults"
    driver.get(reuters_url)
    content = driver.page_source
    pattern = re.compile(r'href: "(?P<urlend>.+)"')
    container_list = pattern.findall(content)

    for container in container_list:
        cur_article = Article()
        href = "https://cn.reutersmedia.net" + container
        cur_article.url = href
        articles.append(cur_article)
    driver.close()
    return articles






def baiduGetUrlSet(key_word) -> set:       #tested
    driver = get_driver()
    container_list = []  # 存放临时URL
    articles = []  # article 集合
    baidu_url_list = ["https://www.baidu.com/s?ie=UTF-8&wd=" + key_word,
                      "https://www.baidu.com/s?ie=UTF-8&tn=news&wd=" + key_word]
    #百度网页搜索与新闻搜索
    for i in range(2):
        driver.get(baidu_url_list[i])
        # 获取每条搜索结果的URL
        for page in range(1, MAX_PAGE + 1):
            BF1 = BF(driver.page_source, 'lxml')
            # print(driver.page_source)
            if i == 0:
                page_container_list = BF1.findAll("div", {"class": re.compile(".*c-container.*")})
            else:
                page_container_list = BF1.findAll("div", {"class": "result"})
            # print(page_container_list)
            container_list.extend(page_container_list)
            #多个页面
            b = driver.find_element_by_xpath("//*[text()='下一页>']").click()
            time.sleep(2)
        if i == 0:
            # print(container_list)
            for container in container_list:
                # print(container)
                try:
                    href = container.find("h3").find("a").get("href")
                    baidu_url = requests.get(url=href, headers=headers, allow_redirects=False)
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
                    try:
                        cur_article.pubtime = container.find("span", {"class": " newTimeFactor_before_abs m"}).get_text()[:-13]
                    except:
                        cur_article.pubtime = ""
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
                    try:
                        cur_article.pubtime = container.find("span", {"class": " newTimeFactor_before_abs m"}).get_text()[
                                          :-17]
                    except:
                        cur_article.pubtime = ""
                    raw_title = container.find("h3", {"class": "c-title"}).find("a").get_text()
                    cur_article.title = re.sub("\"|<em>|</em>", "", raw_title)
                    articles.append(cur_article)
    driver.close()
    return articles


def googleGetUrlSet(key_word) -> set:     #tested
    driver = get_driver()
    google_url_list = ["https://www.google.com.hk/search?q=" + key_word,
                       "https://www.google.com/search?q={}&tbm=nws".format(key_word)]
    container_list = []  # 存放临时URL
    articles = []  # article 集合
    for google_tag in range(0,2):
        try:
            driver.get(google_url_list[google_tag])
        except:
            driver.refresh()
        # 需要刷新一下界面
        time.sleep(2)
        driver.refresh()
        time.sleep(5)
        driver.get(google_url_list[google_tag])
        for page in range(1, MAX_PAGE + 1):
            BF1 = BF(driver.page_source)
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
                        except:
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

            b = driver.find_element_by_xpath("//*[text()='下一页']").click()
            time.sleep(2)
    driver.close()
    return articles


def wikiGeturlSet(key_word) -> list():               #tested
    driver = get_driver()
    wiki_url = "https://zh.wikipedia.org/w/index.php?sort=relevance&profile=advanced&fulltext=1&ns0=1&search="+key_word
    articles = []  # URL集
    driver.get(wiki_url)
    bf1 = BF(driver.page_source, 'lxml')
    container_list = bf1.find_all("li", {"class": "mw-search-result"})
    for container in container_list:
        try:
            imge_url = ""
            href = "https://zh.wikipedia.org/"+container.find("a").get("href")
            title = container.find("a").get_text()
            raw_pubtime = container.find("div", {"class": "mw-search-result-data"}).get_text()
            pattern = re.compile(".*- (.*)")
            pubtime = re.match(pattern, raw_pubtime).group(1)
        except:
            continue
        cur_article = Article()
        cur_article.title = title
        cur_article.img = imge_url
        cur_article.url = href
        cur_article.pubtime = pubtime
        articles.append(cur_article)
    driver.close()
    return articles


def cnnGetUrlSet(key_word) -> set:       #tested
    driver = get_driver()
    articles = []  # URL集
    cnn_url = "https://edition.cnn.com/search?size=20&q="+key_word
    driver.get(cnn_url)
    bf1 = BF(driver.page_source, 'lxml')
    container_list = bf1.find_all("div", {"class": "cnn-search__result cnn-search__result--article"})
    for container in container_list:
        try:
            imge_url = container.find("div", {"class": "cnn-search__result-thumbnail"}).find("img").get("src")
            href = "http:" + container.find("div", {"class": "cnn-search__result-contents"}).find("h3").find("a").get("href")
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
    driver.close()
    return articles


def abcNewsGetUrlSet(key_word) -> set:
    driver = get_driver(0,1)
    articles = []  # URL集
    abcNews_url = "https://abcnews.go.com/search?r=week&searchtext="+key_word
    driver.get(abcNews_url)
    BF1 = BF(driver.page_source)
    container_list = BF1.find_all("div", {"class": re.compile("result.*")})

    for container in container_list:
        try:
            try:
                imge_url = container.find("img").get("src")
            except:
                imge_url = ""
            href = container.find("a", {"class": "title"}).get("href")
            title = container.find("a", {"class": "title"}).get_text()
            driver.get(href)
            html = driver.page_source
            BF1 = BF(html)
            pubtime = BF1.find("span", {"class": re.compile("article-date|timestamp")}).get_text()
        except Exception as e:
            print(e)
            continue
        cur_article = Article()
        cur_article.title = title
        cur_article.img = imge_url
        cur_article.url = href
        cur_article.pubtime = pubtime
        articles.append(cur_article)
    driver.close()
    return articles


def tassGetUrlSet(key_word) -> list:      #tested
    articles = []  # URL集
    driver = get_driver(0, 1, 0)
    tass_url = "http://tass.com/search?sort=date&range=week&searchStr=" + key_word
    driver.get(tass_url)
    BF1 = BF(driver.page_source, 'lxml')
    #print(BF1)
    container_list = BF1.find_all("div", {"data-ng-repeat": re.compile(".*searchResult")})
    #print(container_list)
    for container in container_list:
        try:
            href = "http://www.tass.com" + container.find("a").get("href")
            title = container.find("span", {"class": "news-preview__title ng-binding"}).get_text()
            try:
                imge_url = container.find("div", {"data-ng-if": "item.image"}).find("div").get("style")[23:-2]
            except Exception as e:
                print(e)
                imge_url = ""
            #print(href)
            time.sleep(2)
            driver.get(href)
            html = driver.page_source
            #print(html)
            BF2 = BF(html)
            pubtime = BF2.find("span", {"data-ng-if": "visibleDate", "class": "ng-binding ng-scope"}).get_text()
            #print(pubtime)
        except Exception as e:
            print(e)
            continue
        cur_article = Article()
        cur_article.title = title
        cur_article.img = imge_url
        cur_article.url = href
        cur_article.pubtime = pubtime
        articles.append(cur_article)
    driver.close()
    return articles


def baiduGetArticle(url) -> dict:
    article = dict()
    # do some thing
    return article


def getArticles(articles):
    driver = get_driver(0, 1, 0)
    count = 0
    for article in articles:
        try:
            time.sleep(1)
            try:
                driver.get(article.url)
            except:
                driver.refresh()
            time.sleep(2)
            driver.refresh()
            js = "var q=document.documentElement.scrollTop=100000"
            driver.execute_script(js)
            time.sleep(3)
            text = fulltext(driver.page_source, language='zh')
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
    return articles


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



def get_driver(is_headless=0, is_eager=0, load_images=1):
    options = webdriver.ChromeOptions()
    prefs={
        'profile.default_content_setting_values': {
            'images': load_images,
            #'video':2
        }
    }
    #options.add_argument("--user-data-dir="+r"C:/Users/Liuyus\AppData/Local/Google/Chrome/User Data/")
    options.add_experimental_option('prefs', prefs)
    if is_headless:
        options.add_argument('--headless')
    else:
        pass
    if is_eager:
        desired_capabilities = DesiredCapabilities.CHROME  # 修改页面加载策略
        desired_capabilities["pageLoadStrategy"] = "eager"
    else:
        pass
    driver = webdriver.Chrome(executable_path=r"H:\Github\Crawler-blackout\chromedriver.exe",chrome_options=options)
    return driver
#-------------------------------------------------------end Xu --------------------------------------------------------------




def test():
    #driver = get_driver()
    # s = xinhuaGetUrlSet('停电', num=20)
    #
    # for each_article in s:
    #     print('{:40} {}'.format(each_article.url, each_article.pubtime))
    articles = []
    key = "today"
    articles.extend(baiduGetUrlSet(key))
    articles.extend(googleGetUrlSet(key))
    articles.extend(cnnGetUrlSet(key))
    #articles.extend(tassGetUrlSet(key))       #chrome加载时间太长
    articles.extend(wikiGeturlSet(key))
    #articles.extend(abcNewsGetUrlSet(key))        #大部分？都是视频

    # articles.extend()
    # articles.extend()
    # articles.extend()

    articles = getArticles(articles)
    for article in articles:
        print(article.content)
    print("-------------------------------------------------")

    # print(reutersGetUrlSet("停电"))


test()


