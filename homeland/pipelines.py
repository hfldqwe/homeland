# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import time
from .models.news_model import YibanModel
from .models.filter_url import FilterUrl
import logging


# class HomelandPipeline(object):
#     def open_spider(self,spider):
#         self.yiban = YibanModel()
#         self.filter_url = FilterUrl()
#         self.logger = logging.getLogger()
#
#     def process_item(self, item, spider):
#         spider_time = int(time.time())
#         source_type = "xfjy"
#         block_types = item["position"]
#         title = item["title"]
#         create_time = item["detail_time"]
#         author = item["author"]
#         attachment = item["attch_name_url"]
#         content = item["content"]
#         article_url = item["article_url"]
#
#         for block_type in block_types:
#             passed = self.yiban.filder_news(title,create_time,block_type)
#
#             try:
#                 # 判断是否已经存在，存在就写入日志，然后不用插入数据库
#                 if passed:
#                     self.logger.warning("这篇文章数据库中已存在，文章链接：%s" % article_url)
#                     # 获取新闻的id，然后写入tags
#                     id = self.yiban.id_news(title, create_time, block_type)
#                     self.yiban.tags(block_type, id)
#                 else:
#                     msg = self.yiban.insert_news(source_type,block_type,title,create_time,author,attachment,content,spider_time)
#
#                     if msg:
#                         # 插入数据库失败，error
#                         self.logger.error(msg+","+"文章链接：%s" % article_url)
#                     else:
#                         # 获取新闻的id，然后写入tags
#                         id = self.yiban.id_news(title,create_time,block_type)
#                         self.yiban.tags(block_type,id)
#             except BaseException as e:
#                 self.logger.error("数据库过程中出现错误"+str(e)+"文章链接：%s" % article_url)
#             else:
#                 self.filter_url.add(article_url)


class HomelandPipeline(object):
    def open_spider(self, spider):
        pass

    def process_item(self, item, spider):
        pass


