# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import time
from .models.news_model import YibanModel
from .models.filter_url import FilterUrl
import logging

from .spiders.info_spider import InfoSpider
from .spiders.xfjy_spider import XfjySpider
from .spiders.official_spider import OfficialSpider

from scrapy.exceptions import CloseSpider


class HomelandPipeline:
    def open_spider(self,spider):
        self.logger = logging.getLogger()
        if isinstance(spider,InfoSpider):
            name = "info_article_url"
            self.source_type = spider.source_type
            self.channel_id = 7
        elif isinstance(spider,XfjySpider):
            name = "xfjy_article_url"
            self.source_type = "xfjy"
            self.channel_id = 5
        elif isinstance(spider,OfficialSpider):
            name = "official_artical_url"
            self.source_type = "official"
            self.channel_id = 4
        else:
            self.logger.error("没有找到启动的爬虫,pipelines无法加载，%s" % spider.__class__)
            raise CloseSpider("没有找到启动的爬虫,pipelines无法加载，%s" % spider.__class__)

        self.yiban = YibanModel()
        self.filter_url = FilterUrl(name)

    def process_item(self, item, spider):
        article_url = item.get("article_url")
        img = item.get('img', '')
        if img:
            style = 2
        else:
            style = 0

        power = item.get("power", "all")
        if not power:
            power = "all"

        kwargs_dict = {
            # 额外的参数
            'article_url' : article_url,

            # archives表
            'channel_id' : self.channel_id,
            'model_id' : 1,
            'title' : item["title"],
            'flag' : '',
            'image' : img,
            'attachfile' : item.get("attch_name_url", ''),
            'keywords' : '',
            'description' : '',
            'tags' : item.get('block_type'),
            'weigh' : 0,
            'views' : 0,
            'comments' : 0,
            'likes' : 0,
            'dislikes' : 0,
            'diyname' : '',
            'createtime' : int(time.time()),
            'publishtime' : item.get('detail_time'),
            'status' : 'normal',
            'power' : power,  # 'all'.'student','teacher',

            # addonnews表
            'content' : item.get("content"),
            'author' : item.get("author",""),
            'style' : style,
        }

        try:
            passed = self.yiban.insert_mysql(kwargs_dict=kwargs_dict)
            if passed:
                self.filter_url.add(article_url)
            else:
                self.logger.error("url不在过滤池中，文章却保存到0了数据库")
        except BaseException as e:
            self.logger.error(str(e))
            self.logger.error("数据库交互出现了错误")

