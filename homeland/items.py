# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class HomelandItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    position = scrapy.Field()       # 用来记录当前板块的位置，如：'先锋家园--团学新闻--院系传真--政治'
    title = scrapy.Field()          # 用来记录当前的标题，如：'政治学院召开2015级新生家长见面会{图}'
    attch_name_url = scrapy.Field() # 用来记录附件的title和url，json格式，可能为空，如：'{}'
    author = scrapy.Field()         # 作者，可能为一个空的字符串，如：'张霞'
    content = scrapy.Field()        # 内容
    detail_time = scrapy.Field()    # 一个时间戳，如：1493395740
    article_url = scrapy.Field()    # 文章链接，如：http://xfjy.chd.edu.cn/info/1036/27354.htm






