def baiduGetUrlSet(key_word) -> set:  # tested
    driver = get_driver()
    container_list = []  # 存放临时URL
    articles = []  # article 集合
    baidu_url_list = ["https://www.baidu.com/s?ie=UTF-8&wd=" + key_word,
                      "https://www.baidu.com/s?ie=UTF-8&tn=news&wd=" + key_word]
    # 百度网页搜索与新闻搜索
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
            # 多个页面
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
                        # 有些搜索结果没有图片
                    except:
                        cur_article.img = ""
                    try:
                        cur_article.pubtime = container.find("span",
                                                             {"class": " newTimeFactor_before_abs m"}).get_text()[:-13]
                    except:
                        cur_article.pubtime = ""
                    raw_title = container.find("h3", {"class": "t"}).find("a").get_text()
                    cur_article.title = re.sub("\"|<em>|</em>", "", raw_title)
                    articles.append(cur_article)
                container_list = []
        else:
            for container in container_list:
                href = container.find("h3").find("a").get("href")

                cur_article = Article()
                cur_article.url = href + '\n'
                cur_article.img = ""
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


def googleGetUrlSet(key_word) -> set:  # tested
    driver = get_driver()
    google_url_list = ["https://www.google.com.hk/search?q=" + key_word,
                       "https://www.google.com/search?q={}&tbm=nws".format(key_word)]
    container_list = []  # 存放临时URL
    articles = []  # article 集合
    for google_tag in range(0, 2):
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
