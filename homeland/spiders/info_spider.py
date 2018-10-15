# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from scrapy import FormRequest
import re
import logging
import json
import time

from scrapy.shell import inspect_response
from ..items import HomelandItem


USERNAME = '2017905714'
PASSWORD = '100818'

class InfoSpider(scrapy.Spider):
    name = 'info_spider'
    allowed_domains = ['portal.chd.edu.cn','ids.chd.edu.cn']
    start_urls = ['http://ids.chd.edu.cn/authserver/login?service=http%3A%2F%2Fportal.chd.edu.cn%2F']

    def parse(self, response):
        lt = response.xpath("//input[@name='lt']//@value").extract_first()
        dllt = response.xpath("//input[@name='dllt']//@value").extract_first()
        execution = response.xpath("//input[@name='execution']//@value").extract_first()
        _eventId = response.xpath("//input[@name='_eventId']//@value").extract_first()
        rmShown = response.xpath("//input[@name='rmShown']//@value").extract_first()
        btn = ""

        formdata = {
            "username":USERNAME,
            "password":PASSWORD,
            "lt":lt,
            "dllt":dllt,
            "execution":execution,
            "_eventId":_eventId,
            "rmShown":rmShown,
            "btn":"",
        }
        yield FormRequest("http://ids.chd.edu.cn/authserver/login?service=http%3A%2F%2Fportal.chd.edu.cn%2F",
                          formdata = formdata,
                          callback=self.spider_news,
                          meta={'pageIndex':1},
                          )

    def spider_news(self,response):
        pageIndex = response.meta.get("pageIndex",None)
        if pageIndex:
            url = "http://portal.chd.edu.cn/detach.portal?pageIndex={}&pageSize=&.pmn=view&.ia=false&action=bulletinsMoreView&search=true&groupid=all&.pen=pe65".format(pageIndex)
            # cookiejar = reqponse.headers.getlist('Set-Cookie')

            # 这部分用于提取news的链接并且进行爬取
            article_urls = response.xpath("//ul[@class='rss-container clearFix']//li//a[@class='rss-title']//@href").extract()
            for article_url in article_urls:
                article_url = response.urljoin(article_url)
                yield Request(article_url,callback=self.parse_article,meta={"forbid":True})

            # 一下部分用于爬取下一页
            # 获取新闻总数和页数
            info = response.xpath("//div[@class='pagination-info clearFix']//span//text()").extract_first()
            if info:
                info = re.compile("\d*/\d*").findall(info)[0]
                news_amount, page_amount = info.split("/")
            else:
                self.log("没有找到文章数和页数，版块链接：%s" % response.url,level=logging.ERROR)
                page_amount = int(pageIndex) + 1

            if int(pageIndex) < int(page_amount):
                pageIndex = int(pageIndex) + 1
                yield Request(url,callback=self.spider_news,meta={"pageIndex":pageIndex})
            else:
                self.log("爬取完毕，总页数：{}，终止页数：{}".format(page_amount,pageIndex))

        else:
            self.log("没有获取到页数，当前页面链接：%s" % response.url,level=logging.ERROR)

    def parse_article(self,response):
        item = HomelandItem()

        title = response.xpath("//div[@class='bulletin-title']//text()").extract_first()
        title = title.strip()

        info = response.xpath("//div[@class='bulletin-info']")
        info_text = info.extract_first()
        author = info.xpath(".//span//text()").extract_first()
        block_type = [re.compile("发布部门：(.*?) <").findall(info_text)[0],]
        creat_time = re.compile("发布时间：(.*?)\r\n").findall(info_text)[0]
        creat_time = int(time.mktime(time.strptime(creat_time,'%Y年%m月%d日 %H:%M')))

        # 文章内容
        content = response.xpath("//div[@class='bulletin-content']").extract_first()

        # 附件
        attachments = response.xpath("//div[@class='att_content']//li")
        attachments = {i.xpath(".//text()").extract_first().strip() : i.xpath(".//span//a//@href").extract_first() for i in attachments[1:]}
        attachments = json.dumps(attachments,ensure_ascii=False)

        item["position"] = block_type
        item["title"] = title
        item["attch_name_url"] = attachments
        item["author"] = author
        item["content"] = content
        item["detail_time"] = creat_time
        item["article_url"] = response.url

        yield item




