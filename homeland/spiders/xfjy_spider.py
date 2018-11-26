#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
import time
from uuid import uuid4
import json
import logging
from scrapy.spiders import CrawlSpider,Rule
from scrapy.linkextractors import LinkExtractor
from ..items import HomelandItem
from ..models.filter_url import FilterUrl
from ..items import XfjyItemItem,XfjyArticleItem,ImageItem,WriteSignalItem
from scrapy.loader import ItemLoader

class XfjySpider(CrawlSpider):
    name = "xfjy"
    allowed_demains = ["chd.edu.cn"]
    start_urls = ["http://xfjy.chd.edu.cn/"]

    custom_settings = {
    }

    rules = (
        # 防止取到首页的另一个地址以及一些没用的地址
        Rule(LinkExtractor(unique=True,allow=["xfjy.chd.edu.cn/index.htm","http://xfjy.chd.edu.cn/wmtw.htm",
                                  "http://xfjy.chd.edu.cn/wmtw/zzjg.htm","http://xfjy.chd.edu.cn/wmtw/ryfg.htm",
                                  "http://xfjy.chd.edu.cn/wmtw/twjj.htm"],
                           deny=["xfjy.chd.edu.cn/.*?/\d{1,6}.htm",]
                           )),
        # 取到文件的地址
        Rule(LinkExtractor(unique=True,allow=["http://xfjy.chd.edu.cn/wjhb.htm","http://xfjy.chd.edu.cn/cyxz.htm",
                                  "http://xfjy.chd.edu.cn/wjhb/tfxw.htm",],
                           deny=["xfjy.chd.edu.cn/.*?/\d{1,6}.htm", ]
                           ),
             callback="parse_index"),
        # 取到新闻的地址
        Rule(LinkExtractor(unique=True,allow_domains="xfjy.chd.edu.cn",
                           deny=["xfjy.chd.edu.cn/.*?/\d{1,6}.htm",]
                           ),
             callback="parse_index"),
    )

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        increment = crawler.settings.get("INCREMENT_CRAWL",False)
        spider = super().from_crawler(crawler,increment=increment, *args, **kwargs)
        return spider

    def __init__(self,increment=False,*args,**kwargs):
        super().__init__(*args,**kwargs)

        self.filter = FilterUrl("xfjy_article_url")
        self.increment = increment

        self.order = 1       # 用于存放block_type和index

    def parse_index(self, response):
        url = response.urljoin(response.url)
        if url != "http://xfjy.chd.edu.cn/":
            yield scrapy.Request(url=url,callback=self.parse_item,dont_filter=True,
                                 meta={
                                     "type":"start",
                                     "start_url":response.url
                                 })

    def _next_request(self,response,start_url):
        ''' 返回下一页爬取的request对象或者此版块爬取完成返回一个None '''
        start_url = start_url

        next_url = response.css(".Next::attr(href)").extract_first()
        if next_url:
            next_url = response.urljoin(next_url)
            return Request(next_url, callback=self.parse_item, dont_filter=True,
                                 meta={"type": "item", "start_url": start_url})
        else:
            self.log("此版块爬取结束")

    def _article_requests(self,response):
        index = self.order

        request_list = []  # 用来存放返回的request对象
        loader = ItemLoader(item=XfjyItemItem(), response=response)
        loader.add_xpath("tags_list", "string(//div[@class='weizhi']//td)")

        tags_list = loader.get_output_value("tags_list")

        # 解析出文章title，date，url，并且进行文章爬取
        tr_tags = response.xpath("//div[@class='main_nei_you_baio_content']//tr[@height='20']")
        for tr_tag in tr_tags:
            # 提取文章的url,并且拼接为完整的链接
            url = tr_tag.xpath(".//a//@href").extract_first()
            if url:
                url = response.urljoin(url)
            else:
                self.log("没有解析到文章url，板块链接：%s" % response.url, level=logging.ERROR)

            # 将title提取出来并且进行解析
            title = tr_tag.xpath(".//a//@title").extract_first()
            if title:
                title = "".join(title.split())
            else:
                self.log("没有解析到title，板块链接：%s" % response.url, level=logging.WARNING)

            # 将date提取出来，并且进行解析成时间戳
            date = tr_tag.xpath(".//span[@class='timestyle44007']//text()").extract_first()
            if date:
                date = int(time.mktime(time.strptime("".join(date.split()), "%Y年%m月%d日")))
            else:
                self.log("没有解析到date，板块链接：%s" % response.url, level=logging.WARNING)
                date = None

            exist = self.filter.filter(url)
            if not exist:
                request = Request(url,
                                  meta={"title": title, "date": date, "tags_list": tags_list, "type": "article","index":index},
                                  callback=self.parse_article,
                                  )
                request_list.append(request)
                index += 1
        return request_list

    def parse_item(self, response):
        '''
        用来解析爬取的各个板块，收集板块地址和本页文章链接，以及进行下一页爬取,回调
        :param response:
        :return:position,title_dates
        '''
        start_url = response.meta.get("start_url")
        write_item = WriteSignalItem()

        request_list = self._article_requests(response)
        if not request_list and self.increment:
            self.log("增量爬取")

            write_item["write"] = True
            yield write_item

            yield Request(url=start_url,callback=self.parse_item,dont_filter=True,
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

    def parse_article(self, response):
        loader = ItemLoader(item=XfjyArticleItem(),response=response)

        article_url = response.url
        title = response.meta["title"]
        # date = response.meta["date"]
        tags_list = response.meta["tags_list"]
        block_type = ",".join(tags_list)

        # 暂时attachments放在这里
        attchments = response.xpath("//div[@class='main_nei_you_baio_content']//span//a")
        names_urls = [(attchment.xpath(".//span//text()").extract_first(), attchment.xpath(".//@href").extract_first()) for attchment in attchments]
        name_url = {name: response.urljoin(url) for name, url in names_urls}
        attchments= json.dumps(name_url, ensure_ascii=False)

        index = response.meta.get("index")

        loader.add_value("article_url", article_url)
        loader.add_value("title",title)
        loader.add_value("tags_list",tags_list)
        loader.add_value("block_type",block_type)
        loader.add_value("attch_name_url",attchments)
        loader.add_xpath("author","//div[@class='main_nei_you_baio_content']//span[@class='authorstyle44003']//text()")
        loader.add_value("content",response.xpath("//div[@class='main_nei_you_baio_content']//td[@class='contentstyle44003']"))
        loader.add_xpath("img", "//div[@class='main_nei_you_baio_content']//td[@class='contentstyle44003']//@src")
        loader.add_xpath("detail_time","//div[@class='main_nei_you_baio_content']//span[@class='timestyle44003']//text()")
        loader.add_value("index",index)

        imgs = loader.get_collected_values("img")
        if imgs:
            for img in imgs:
                if "http" in img:
                    yield Request(img,callback=self.parse_img,dont_filter=True,meta={"type":"image","article_url":response.url})

        yield loader.load_item()

    def parse_img(self, response):
        image_item = ImageItem()

        image_item["img"] = response.body
        image_item["name"] = response.url
        image_item["article_url"] = response.meta.get("article_url")
        image_item["image_url"] = response.url

        if not response.body:
            yield Request(response.url, callback=self.parse_img, dont_filter=True,
                          meta={"type": "image", "article_url": image_item["article_url"]})
        yield image_item







