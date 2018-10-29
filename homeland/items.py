# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst,MapCompose,Join
import time


def dispose_time(time_str):
    tupletime = time.strptime(time_str,'发布时间：%Y-%M-%d')
    return int(time.mktime(tupletime))

def urljoin_img(img,loader_context):
    ''' 用来补全context链接的 '''
    return loader_context['response'].urljoin(img)

def urljoin_content(content,loader_context):
    ''' 将文章中的链接补全 '''
    response = loader_context['response']
    img_links = content.xpath(".//@src").extract()
    content = content.extract()
    for img_link in img_links:
        content = content.replace(img_link, response.urljoin(img_link))
    return content

class HomelandItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    block_type = scrapy.Field()             # 用来记录当前板块的位置，如：'先锋家园--团学新闻--院系传真--政治'
    title = scrapy.Field()                  # 用来记录当前的标题，如：'政治学院召开2015级新生家长见面会{图}'
    attch_name_url = scrapy.Field()         # 用来记录附件的title和url，json格式，可能为空，如：'{}'
    author = scrapy.Field()                 # 作者，可能为一个空的字符串，如：'张霞'
    content = scrapy.Field()                # 内容
    detail_time = scrapy.Field()            # 一个时间戳，如：1493395740
    article_url = scrapy.Field()            # 文章链接，如：http://xfjy.chd.edu.cn/info/1036/27354.htm\
    img = scrapy.Field()                    #第一个图片地址
    power = scrapy.Field()                  # 允许谁看,权限
    tags_list = scrapy.Field()              # 这个专门用于tags表的标签

class OfficialItem(scrapy.Item):
    block_type = scrapy.Field(output_processor=Join())
    title = scrapy.Field(output_processor=TakeFirst())
    author = scrapy.Field(output_processor=TakeFirst())
    content = scrapy.Field(input_processor=MapCompose(urljoin_content), output_processor=TakeFirst())
    detail_time = scrapy.Field(input_processor=MapCompose(str.strip,dispose_time) , output_processor=TakeFirst())
    article_url = scrapy.Field(output_processor=TakeFirst())
    img = scrapy.Field(input_processor=MapCompose(urljoin_img),output_processor=TakeFirst())
    power = scrapy.Field(output_processor=TakeFirst())  # 允许谁看,权限
    tags_list = scrapy.Field()  # 这个专门用于tags表的标签




