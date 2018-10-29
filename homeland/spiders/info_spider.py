# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from scrapy import FormRequest
import re
import logging
import json
import time

from ..items import HomelandItem
from ..models.filter_url import FilterUrl

class InfoSpider(scrapy.Spider):
    name = 'info'
    allowed_domains = ['portal.chd.edu.cn','ids.chd.edu.cn']
    start_urls = ['http://ids.chd.edu.cn/authserver/login?service=http%3A%2F%2Fportal.chd.edu.cn%2F']

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        increment = crawler.settings.get("INCREMENT_CRAWL",False)
        return cls(increment=increment,*args,**kwargs)

    def __init__(self,username,password,source_type,increment=False,*args,**kwargs):
        super(InfoSpider,self).__init__(*args,**kwargs)
        self.username = username
        self.password = password
        self.source_type = source_type
        if self.source_type == "info":
            self.power = "all"
        elif self.source_type == "info-teacher":
            self.power = "teacher"
        else:
            self.power = "all"

        self.login_url = 'http://ids.chd.edu.cn/authserver/login?service=http%3A%2F%2Fportal.chd.edu.cn%2F'
        self.interval_time = time.time()
        self.repetition = []
        self.filter = FilterUrl("info_article_url")

        self.increment = increment

    def parse(self, response):
        lt = response.xpath("//input[@name='lt']//@value").extract_first()
        dllt = response.xpath("//input[@name='dllt']//@value").extract_first()
        execution = response.xpath("//input[@name='execution']//@value").extract_first()
        _eventId = response.xpath("//input[@name='_eventId']//@value").extract_first()
        rmShown = response.xpath("//input[@name='rmShown']//@value").extract_first()
        btn = ""

        formdata = {
            "username":self.username,
            "password":self.password,
            "lt":lt,
            "dllt":dllt,
            "execution":execution,
            "_eventId":_eventId,
            "rmShown":rmShown,
            "btn":btn,
        }
        yield FormRequest("http://ids.chd.edu.cn/authserver/login?service=http%3A%2F%2Fportal.chd.edu.cn%2F",
                          formdata = formdata,
                          callback=self.spider_news,
                          meta={'pageIndex':0},
                          )

    def spider_news(self,response):
        pageIndex = response.meta.get("pageIndex",None)
        next_url = "http://portal.chd.edu.cn/detach.portal?pageIndex={}&pageSize=&.pmn=view&.ia=false&action=bulletinsMoreView&search=true&groupid=all&.pen=pe65".format(
            pageIndex + 1)

        if pageIndex == 0:
            yield Request(next_url,callback=self.spider_news,meta={'pageIndex':1},dont_filter=True)
        else:

            # 这部分用于提取news的链接并且进行爬取
            article_urls = response.xpath(
                "//ul[@class='rss-container clearFix']//li//a[@class='rss-title']//@href").extract()
            for article_url in article_urls:
                article_url = response.urljoin(article_url)
                if self.filter.filter(article_url):
                    self.repetition.append(article_url)
                else:
                    yield Request(article_url, callback=self.parse_article, meta={"type": "article"})

            # 进行下一页的爬取，或者重复首页增量爬取
            if self.repetition and self.increment:
                self.repetition = []  # 使repetition复原
                self.log("增量爬取",level=logging.DEBUG)
                interval_time = time.time() - self.interval_time
                if interval_time >= 7200:
                    yield Request(self.login_url,callback=self.parse,dont_filter=True)
                yield Request(next_url, callback=self.spider_news, dont_filter=True,
                              meta={'pageIndex': 0})
            else:
                info = response.xpath("//div[@class='pagination-info clearFix']//span//text()").extract_first()
                if info:
                    info = re.compile("\d*/\d*").findall(info)[0]
                    news_amount, page_amount = info.split("/")

                    if int(page_amount) > pageIndex:
                        pageIndex += 1
                        yield Request(next_url, callback=self.spider_news, meta={'pageIndex': pageIndex})
                    else:
                        self.log("信息门户爬取结束，爬取页数{}".format(pageIndex), level=logging.WARNING)

                else:
                    self.log("没有找到文章数和页数，版块链接：%s" % response.url,level=logging.ERROR)
                    yield

    def parse_article(self,response):
        item = HomelandItem()

        title = response.xpath("//div[@class='bulletin-title']//text()").extract_first()
        title = title.strip()

        info = response.xpath("//div[@class='bulletin-info']")
        info_text = info.extract_first()
        author = info.xpath(".//span//text()").extract_first()
        block_type = re.compile("发布部门：(.*?) <").findall(info_text)[0]
        creat_time = re.compile("发布时间：(.*?)\r\n").findall(info_text)[0]
        creat_time = int(time.mktime(time.strptime(creat_time,'%Y年%m月%d日 %H:%M')))

        # 文章内容
        content = response.xpath("//div[@class='bulletin-content']")
        if content:
            img_links = content[0].xpath(".//@src").extract()
            img = [response.urljoin(img_link) for img_link in img_links]
            content = content.extract_first()
            for img_link in img_links:
                content = content.replace(img_link,response.urljoin(img_link))
        else:
            self.log("没有解析到文章内容，文章链接：%s" % response.url)

        # 附件
        attachments = response.xpath("//div[@class='att_content']//li")
        attachments = {i.xpath(".//text()").extract_first().strip() : i.xpath(".//span//a//@href").extract_first() for i in attachments[1:]}
        attachments = json.dumps(attachments,ensure_ascii=False)

        item["block_type"] = block_type
        item["tags_list"] = ["长大官网",block_type]
        item["title"] = title
        item["attch_name_url"] = attachments
        item["author"] = author
        item["content"] = content
        if img:
            item["img"] = img[0].replace("///","//")
        else:
            item["img"] = ""
        item["detail_time"] = creat_time
        item["article_url"] = response.url
        item["power"] = self.power

        yield item




