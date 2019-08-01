from datetime import datetime
from time import sleep
import CrawlerFuncs


class CrawlerFactory:

    def __init__(
            self,
            key,
            lang,
            get_urlset_func,
            get_article_func,

    ):
        self.key = key
        self.searchtime = datetime.now()
        self.lang = lang
        self.get_urlset_func = get_urlset_func
        self.get_article_func = get_article_func


    def getUrlSet(self):
        getUrlSetFunc = self.get_urlset_func
        self.url_set = getUrlSetFunc(self.key)

    def getArticles(self, wait=1):

        getArticleFunc = self.get_article_func
        articles = list()

        for each_article in self.url_set:
            each_article = getArticleFunc(each_article)

            # 此处先行取消sleep，有待结构化
            # sleep(wait)

            each_article.searchtime = self.searchtime
            each_article.key = self.key

            articles.append(each_article)

        return articles
