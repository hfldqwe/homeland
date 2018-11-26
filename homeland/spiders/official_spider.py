# -*- coding: utf-8 -*-

import scrapy
import logging
from scrapy.http import Request
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose
from ..items import OfficialItem,ImageItem,WriteSignalItem
import time
from ..models.filter_url import FilterUrl


class OfficialSpider(scrapy.Spider):
    name = 'official'
    allowed_domains = ['news.chd.edu.cn']

    custom_settings = {
    }

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        increment = crawler.settings.get("INCREMENT_CRAWL",False)
        spider = super().from_crawler(crawler, increment=increment, *args, **kwargs)
        return spider

    def __init__(self,increment=False,*args,**kwargs):
        self.increment = increment
        self.filter = FilterUrl(name="official_article_url")
        self.repetition = []

        self.start_urls = ['http://news.chd.edu.cn/300/list.htm',
                      'http://news.chd.edu.cn/301/list.htm',
                      'http://news.chd.edu.cn/xsxx1/list.htm',
                      'http://news.chd.edu.cn/303/list.htm',
                      'http://news.chd.edu.cn/304/list.htm',
                      'http://news.chd.edu.cn/305/list.htm']

        self.order = 1

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url=url,
                          callback=self.parse,
                          dont_filter=True,
                          meta={
                              "type":"start",
                              'start_url':url,
                          })

    def parse(self,response):
        write_item = WriteSignalItem()
        start_url = response.meta.get("start_url")

        # 如果request_list不为空，那么将进行request_list中的request放入队列进行爬取
        # 否则重复开始页面爬取，直到有新的文章。
        request_list = self._article_requests(response)
        if not request_list and self.increment:
            self.log("增量爬取")

            write_item["write"] = True
            yield write_item

            yield Request(url=start_url,callback=self.parse,dont_filter=True,
                          priority=-1,
                          meta={
                              "type": "start",
                              "start_url":start_url,
                          })
        else:
            for request in request_list:
                yield request

            self.order += len(request_list)

            yield self._next_request(response,start_url)

    def parse_article(self,response):
        loader = ItemLoader(item=OfficialItem(),response=response)

        index = response.meta.get("index")
        title = response.meta.get('title',None)
        tags_list = response.meta.get('tags_list')
        block_type = ",".join(tags_list)

        # 文章中需要提取的信息，标题，详细时间，内容，作者，来源
        article = response.xpath("//div[@class='article']")
        if not title:
            loader.add_xpath("title",".//h1[@class='arti-title']//text()")
        else:
            loader.add_value("title",title)
        article_metas = article.xpath(".//p[@class='arti-metas']//span//text()").extract()
        loader.add_value("detail_time",article_metas[0])
        loader.add_value("author",article_metas[1],re='作者：(.*)')
        loader.add_value("block_type",block_type)
        loader.add_value("content",response.xpath("//div[@id='content']"))
        loader.add_xpath("img","//div[@id='content']//@src")
        loader.add_value("article_url",response.url)
        loader.add_value("tags_list",tags_list)
        loader.add_value("index",index)

        imgs = loader.get_collected_values("img")
        if imgs:
            for img in imgs:
                if "http" in img:
                    yield Request(img, callback=self.parse_img, dont_filter=True,
                                  meta={"type": "image", "article_url": response.url})

        yield loader.load_item()

    def parse_img(self, response):
        image_item = ImageItem()

        image_item["img"] = response.body
        image_item["name"] = response.url
        image_item["article_url"] = response.meta.get("article_url")
        image_item["image_url"] = response.url

        if not response.body:
            self.logger.error("尝试重新爬取图片地址")
            yield Request(response.url, callback=self.parse_img, dont_filter=True,
                          meta={"type": "image", "article_url": image_item["article_url"]})

        yield image_item


    def _article_requests(self,response):
        index = self.order
        request_list = []   # 用来存放返回的request对象

        # 提取出标题，日期和url
        title_date_url = response.xpath("//div[@id='wp_news_w9']//a")
        title_date_url = [(*(i.xpath(".//span//text()").extract()), i.xpath(".//@href").extract_first()) for i in
                          title_date_url]
        # 爬取tag
        tags_list = response.xpath("//div[@class='list-head']//h2[@class='column-title']//text()").extract()

        # 爬取本页面上所有的文章标题，日期，并进行文章爬取
        for title,date,url in title_date_url:
            article_url = response.urljoin(url)
            exist = self.filter.filter(article_url)
            if not exist:
                request = Request(url=article_url, callback=self.parse_article,
                              meta={
                                  'title': title,
                                  'type': 'article',
                                  'tags_list': tags_list,
                                  'index':index
                              })
                request_list.append(request)
                index += 1

        return request_list

    def _next_request(self,response,start_url):
        # 当前页面的一些基本信息，页数，总页数，总文章数，下一页的链接,tags_list
        info = response.xpath("//div[@id='wp_paging_w9']//ul")

        next_url = info.xpath(".//li[@class='page_nav']//a[@class='next']//@href").extract_first()
        current = info.xpath(".//li[@class='page_jump']//em[@class='curr_page']//text()").extract_first()
        end = info.xpath(".//li[@class='page_jump']//em[@class='all_pages']//text()").extract_first()

        # 进行下一页的爬取，或者结束爬取
        if 'javascript' in next_url:
            if int(current) == int(end):
                self.log("本页爬取正常结束,链接：{}".format(response.url), level=logging.DEBUG)
            else:
                self.log("本页爬取异常结束,链接：{}".format(response.url), level=logging.ERROR)
        else:
            next_url = response.urljoin(next_url)
            return Request(next_url, callback=self.parse,
                          meta={
                              "type": "item",
                              "start_url" : start_url,
                          })
