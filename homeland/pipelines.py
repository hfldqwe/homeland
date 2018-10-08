# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import time
from .models.news_model import YibanModel


class HomelandPipeline(object):
    def open_spider(self,spider):
        self.yiban = YibanModel()

    def process_item(self, item, spider):
        '''
        spider_time = int(time.time())
        source_type = "xfjy"
        block_type = item["position"]
        title = item["title"]
        create_time = item["detail_time"]
        author = item["author"]
        attachment = item["attch_name_url"]
        content = item["content"]
        '''

        spider_time = int(time.time())
        source_type = "xfjy"
        block_types = item["position"]
        title = item["title"]
        create_time = item["detail_time"]
        author = item["author"]
        attachment = item["attch_name_url"]
        content = item["content"]

        for block_type in block_types:
            self.yiban.insert(source_type,block_type,title,create_time,author,attachment,content,spider_time)
