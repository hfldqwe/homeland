# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class OfficialSpider(CrawlSpider):
    name = 'official'
    allowed_domains = ['chd.edu.cn']
    start_urls = ['http://chd.edu.cn/']

    rules = (
        Rule(LinkExtractor(allow=r'http://news.chd.edu.cn'),callback='parse_news',follow=True),
        Rule(LinkExtractor(allow="http://www.chd.edu.cn"),callback='parse_items',follow=True),
    )

    def parse_item(self, response):
        self.log("item链接：")
        self.log(response.url)

    def parse_news(self, response):
        self.log("news链接:")
        self.log(response.url)
