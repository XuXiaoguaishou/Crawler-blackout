"""
    文章类，目前包含以下属性：
        title：      文章标题
        pubtime：    发表时间
        content：    文章内容
        url：        网络url
        site：       所属网站
        key：        搜索该文章时所用关键字
        searchtime： 搜索该文章时的时间
        img：        一张代表图片的url
        flag：       是否被采用
        lang：       所属语言类型
"""


class Article:

    """
        此处的字段定义应考虑移植到Django中；
    """

    # 必须在siteGetUrlSet()中完成定义
    url = ''

    # 必须在siteGetArticle()中完成定义
    content = ''
    site = ''
    lang = ''

    # 可选定义，在以上两个函数任意一个内定义
    title = ''
    pubtime = ''
    img = ''

    # 在爬虫构造中完成定义
    key = ''
    searchtime = ''

    # 暂时放置
    flag = False

    def __init__(self):
        """
            Article对象的成员全部在外部定义
        """
        pass

    def __str__(self):
        pass

    def __eq__(self, other_article):
        """
            判断两文章对象的唯一条件即使他们是否有相同的Url
        """
        return self.url == other_article.url
