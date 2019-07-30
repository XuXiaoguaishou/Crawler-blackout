from datetime import datetime
from time import sleep
import crawlerfuncs


class CrawlerBuilder:

    def __init__(
            self,
            key,
            lang,
            get_urlset_func,
            get_article_func,
            time=datetime.now(),
    ):
        self.key = key
        self.time = time
        self.lang = lang
        self.get_urlset_func = get_urlset_func
        self.get_article_func = get_article_func

    def getUrlSet(self):
        getUrlSetFunc = self.get_urlset_func
        self.url_set = getUrlSetFunc(self.key)

    def getArticles(self, wait=1):

        getArticleFunc = self.get_article_func
        articles = list()

        for each_url in self.url_set:
            each_article = getArticleFunc(each_url)

            sleep(wait)

            each_article['time'] = self.time
            each_article['key'] = self.key
            each_article['url'] = each_url

            articles.append(each_article)

        return articles

