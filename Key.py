"""
    关键词类，目前包含以下属性：
        language：   语言
        key：        内容
        search_record：搜索记录编号
"""
from django.db import models

class Key:
    LANGUAGE_ITEMS = [
        (0, "CN"),
        (1, "EN"),
    ]
    search_record = models.ForeignKey(SearchRecord, verbose_name="search_record")
    key = models.CharField(max_length=128, verbose_name="key")
    language = models.IntegerField(choices=LANGUAGE_ITEMS, default=0, verbose_name="language")

    class Meta:
        verbose_name = verbose_name_plural = "Key"

