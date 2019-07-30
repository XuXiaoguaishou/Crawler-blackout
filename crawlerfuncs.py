"""
    该文件放置各网站不同的的爬取策略方法
    每个网站site的策略方法应成对编写 siteGetUrlset 与 siteGetArticle 两个方法
    之后按 'site': (siteGetUrlset, siteGetArticle) 放置在常量字典 FUNCS 中

    siteGetUrlSet( key, num=10) -> urlset:
        :param str key: 搜索关键字，与停电内容相关
        :param int num: 指定结果最大收录的文章数量
        :return set urlset: 该站对key搜索的结果链接集合, 其长度 <= num(当所有文章无重时取等于)

    siteGetArticle( url) -> article:
        :param str url: 文章url
        :return str article: 一个字典。其中包含了这篇文章的以下信息：
            article{
                'title':    str 文章标题,
                'content':  str 文章内容，
                'site':     str 来源站点，
                'image':    str 一张代表图片的url
            }
"""

pass


def baiduGetUrlSet(key, num=10) -> set:
    urlset = set()
    # do some thing
    return urlset


def baiduGetArticle(url) -> dict:
    article = dict()
    # do some thing
    return article


FUNCS = {
    'baidu': (baiduGetUrlSet, baiduGetArticle)
}
