#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import scrapy
import time
import json
import logging
from scrapy.spiders import CrawlSpider,Rule
from scrapy.linkextractors import LinkExtractor
from ..items import HomelandItem
import re

class XfjySpider(CrawlSpider):
    name = "xfjy"
    allowed_demains = ["chd.edu.cn"]
    start_urls = ["http://xfjy.chd.edu.cn/"]

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
                           ),callback="parse_index"),
        # 取到新闻的地址
        Rule(LinkExtractor(unique=True,allow_domains="xfjy.chd.edu.cn",
                           deny=["xfjy.chd.edu.cn/.*?/\d{1,6}.htm",]
                           ),callback="parse_index"),
    )

    def parse_index(self, response):
        url = response.urljoin(response.url)
        if url != "http://xfjy.chd.edu.cn/":
            yield scrapy.Request(url=url,callback=self.parse_item,dont_filter=True)

    def parse_item(self, response):
        '''
        用来解析爬取的各个板块，收集板块地址和本页文章链接，以及进行下一页爬取,回调
        :param response:
        :return:position,title_dates
        '''
        amount_item = response.meta.get("amount_item",0)

        # 将位置（板块名称）进行解析组合成为我们需要的名称
        position = response.xpath("string(//div[@class='weizhi']//td)").extract_first()
        position = "".join(position.split()).split(">>")
        position[0] = "先锋家园"

        # 解析出文章title，date，url，并且进行文章爬取
        tr_tags = response.xpath("//div[@class='main_nei_you_baio_content']//tr[@height='20']")
        amount_item += len(tr_tags)
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

            yield scrapy.Request(url, meta={"title": title, "date": date, "position": position,"forbid":True},
                                 callback=self.parse_article)

        next_url = response.css(".Next::attr(href)").extract_first()
        if next_url:
            next_url = response.urljoin(next_url)
            yield scrapy.Request(next_url,callback=self.parse_item,meta={"amount_item":amount_item})
        else:
            # 解析当前版块的文章条数
            try:
                amount = response.xpath(
                    "//div[@class='main_nei_you_baio_content']//td[@id='fanye44007']//text()").extract_first()
                amount = re.compile("共(.*?)条").findall(amount)[0]
            except:
                amount = 0
            if int(amount_item) != int(amount):
                self.log("爬取数量不对应，版块链接：{}，应爬：{} / 实爬：{}".format(response.url,amount,amount_item),level=logging.ERROR)


    def parse_article(self, response):
        item = HomelandItem()

        title = response.meta["title"]
        date = response.meta["date"]
        position = response.meta["position"]

        article_url = response.url

        # 用来解析title和url
        attchments = response.xpath("//div[@class='main_nei_you_baio_content']//span//a")
        names_urls = [(attchment.xpath(".//span//text()").extract_first(),attchment.xpath(".//@href").extract_first()) for attchment in attchments]
        name_url = {name:response.urljoin(url) for name,url in names_urls}
        attch_name_url = json.dumps(name_url,ensure_ascii=False)

        # 解析出来author
        author = response.xpath("//div[@class='main_nei_you_baio_content']//span[@class='authorstyle44003']//text()").extract_first()
        if author:
            author = "".join(author.split())

        # 对content进行处理
        content = response.xpath("//div[@class='main_nei_you_baio_content']//td[@class='contentstyle44003']")
        if content:
            img_links = content[0].xpath(".//@src").extract()
            content = content.extract_first()
            for img_link in img_links:
                content = content.replace(img_link,response.urljoin(img_link))
        else:
            self.log("没有解析到文章内容，文章链接：%s" % response.url)

        # 提取发布时间
        try:
            detail_time = response.xpath("//div[@class='main_nei_you_baio_content']//span[@class='timestyle44003']//text()").extract_first()
            detail_time = "".join(detail_time.split())
            detail_time = int(time.mktime(time.strptime(detail_time,"%Y-%m-%d%H:%M")))
        except:
            self.log("没有解析到文章详细时间，文章链接：%s" % response.url)
            detail_time = date

        item["position"] = position
        item["title"] = title
        item["attch_name_url"] = attch_name_url
        item["author"] = author
        item["content"] = content
        item["detail_time"] = detail_time
        item["article_url"] = article_url

        '''
        字段名对应的item字段名
        spider_time = int(time.time())
        source_type = "xfjy"

        block_type = item["position"]
        title = item["title"]
        create_time = item["detail_time"]
        author = item["author"]
        attachment = item["attch_name_url"]
        content = item["content"]
        '''

        yield item


# 不知道为何在parser_item中进行调用，没有效果，直接写在里面就可以了，所以暂时不删除以下代码，希望找到bug后改回来
    # def dispose(self,response,position):
    #     '''
    #     对板块的数据做进一步的处理,在parse_item中进行调用
    #     '''
    #     tr_tags = response.xpath("//div[@class='main_nei_you_baio_content']//tr[@height='20']")
    #
    #     for tr_tag in tr_tags:
    #         # 提取文章的url,并且拼接为完整的链接
    #         url = tr_tag.xpath(".//a//@href").extract_first()
    #         if url:
    #             url = response.urljoin(url)
    #         else:
    #             self.log("没有解析到文章url，板块链接：%s" % response.url, level=logging.ERROR)
    #
    #         # 将title提取出来并且进行解析
    #         title = tr_tag.xpath(".//a//@title").extract_first()
    #         if title:
    #             title = "".join(title.split())
    #         else:
    #             self.log("没有解析到title，板块链接：%s" % response.url,level=logging.WARNING)
    #
    #         # 将date提取出来，并且进行解析成时间戳
    #         date = tr_tag.xpath(".//span[@class='timestyle44007']//text()").extract_first()
    #         if date:
    #             date = int(time.mktime(time.strptime("".join(date.split()), "%Y年%m月%d日")))
    #         else:
    #             self.log("没有解析到date，板块链接：%s" % response.url, level=logging.WARNING)
    #             date = None
    #
    #         yield scrapy.Request(url,meta={"title":title,"date":date,"position":position},callback=self.parse_article,dont_filter=True)






