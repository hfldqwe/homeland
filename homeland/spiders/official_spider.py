# -*- coding: utf-8 -*-

import scrapy
import logging
from scrapy.http import Request
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose
from ..items import OfficialItem

from scrapy.shell import inspect_response

class OfficialSpider(scrapy.Spider):
    name = 'official'
    allowed_domains = ['news.chd.edu.cn']
    start_urls = ['http://news.chd.edu.cn/300/list.htm',
                  'http://news.chd.edu.cn/301/list.htm',
                  'http://news.chd.edu.cn/xsxx1/list.htm',
                  'http://news.chd.edu.cn/303/list.htm',
                  'http://news.chd.edu.cn/304/list.htm',
                  'http://news.chd.edu.cn/305/list.htm']

    custom_settings = {
        'DOWNLOAD_DELAY':0,
    }

    def parse(self,response):
        articles_url_title = response.xpath("//div[@id='wp_news_w9']//a")
        article_url_title = [( *(i.xpath(".//span//text()").extract()) , i.xpath(".//@href").extract_first()) for i in articles_url_title]

        # 爬取本页面上所有的文章标题，日期，并进行下一页爬取
        for title,date,url in article_url_title:
            article_url = response.urljoin(url)
            yield Request(url=article_url,callback=self.parse_article,
                          meta={
                              'title':title,
                          })

        # 当前页面的一些基本信息，页数，总页数，总文章数，下一页的链接
        info = response.xpath("//div[@id='wp_paging_w9']//ul")
        page = info.xpath(".//li[@class='pages_count']//em[@class='per_count']//text()").extract_first()
        amount = info.xpath(".//li[@class='pages_count']//em[@class='all_count']//text()").extract_first()

        next_url = info.xpath(".//li[@class='page_nav']//a[@class='next']//@href").extract_first()

        current = info.xpath(".//li[@class='page_jump']//em[@class='curr_page']//text()").extract_first()
        end = info.xpath(".//li[@class='page_jump']//em[@class='all_pages']//text()").extract_first()

        # 进行下一页爬取或者结束
        if 'javascript' in next_url and int(current) == int(end):
            self.log("本页爬取正常结束,链接：{}".format(response.url),level=logging.DEBUG)
        elif 'javascript' in next_url or int(current) == int(end):
            self.log("本页爬取异常结束,链接：{}".format(response.url),level=logging.ERROR)
        else:
            next_url = response.urljoin(next_url)
            yield Request(next_url,callback=self.parse)

    def parse_article(self,response):
        loader = ItemLoader(item=OfficialItem(),response=response)

        title = response.meta.get('title',None)

        # 文章中需要提取的信息，标题，详细时间，内容，作者，来源
        article = response.xpath("//div[@class='article']")
        if not title:
            loader.add_xpath("title",".//h1[@class='arti-title']//text()")
        else:
            loader.add_value("title",title)

        article_metas = article.xpath(".//p[@class='arti-metas']//span//text()").extract()

        loader.add_value("detail_time",article_metas[0])
        loader.add_value("author",article_metas[1],re='作者：(.*)')
        loader.add_value("block_type",article_metas[2],re='来源：(.*)')
        loader.add_value("block_type","长大官网")

        loader.add_xpath("content",".//div[@id='content']")

        loader.add_value("article_url",response.url)

