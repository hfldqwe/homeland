# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.http import Request
from scrapy import FormRequest
from scrapy.shell import inspect_response
from scrapy.http.cookies import CookieJar
import re
import time
import logging
import json
import time

from ..items import HomelandItem,ImageItem,WriteSignalItem
from ..models.filter_url import FilterUrl

cookiejar = CookieJar()

class InfoSpider(scrapy.Spider):
    name = 'info'
    allowed_domains = ['portal.chd.edu.cn','ids.chd.edu.cn']

    custom_settings = {
    }

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        increment = crawler.settings.get("INCREMENT_CRAWL",False)
        spider = super().from_crawler(crawler, increment=increment, *args, **kwargs)
        return spider

    def __init__(self,username,password,source_type,increment=False,*args,**kwargs):
        super(InfoSpider,self).__init__(*args,**kwargs)
        self.username = username
        self.password = password

        self.source_type = source_type
        if self.source_type == "info":
            self.power = "all"
            redis_name = "info_article_url"
        elif self.source_type == "info-teacher":
            self.power = "teacher"
            redis_name = "infoteacher_article_url"
        else:
            self.power = "all"
            redis_name = "info_article_url"

        self.login_url = 'http://ids.chd.edu.cn/authserver/login?service=http%3A%2F%2Fportal.chd.edu.cn%2F'
        self.start_url = "http://portal.chd.edu.cn/detach.portal?.pmn=view&.ia=false&action=bulletinsMoreView&search=true&.f=f40571&.pen=pe65&groupid=all"
        self.interval_time = time.time()
        self.repetition = []
        self.filter = FilterUrl(redis_name)

        self.increment = increment

        self.order = 1   # 键是block_type，值为index

    def start_requests(self):
        yield Request(url=self.login_url,dont_filter=True,callback=self.login,
                      meta={"type":"start",
                            "start_url":self.start_url})

    def _login(self,response):
        lt = response.xpath("//input[@name='lt']//@value").extract_first()
        dllt = response.xpath("//input[@name='dllt']//@value").extract_first()
        execution = response.xpath("//input[@name='execution']//@value").extract_first()
        _eventId = response.xpath("//input[@name='_eventId']//@value").extract_first()
        rmShown = response.xpath("//input[@name='rmShown']//@value").extract_first()
        btn = ""

        formdata = {
            "username": self.username,
            "password": self.password,
            "lt": lt,
            "dllt": dllt,
            "execution": execution,
            "_eventId": _eventId,
            "rmShown": rmShown,
            "btn": btn,
        }
        return FormRequest("http://ids.chd.edu.cn/authserver/login?service=http%3A%2F%2Fportal.chd.edu.cn%2F",
                          formdata=formdata,
                          callback=self.parse_item,dont_filter=True,
                          )

    def login(self, response):
        login_request = self._login(response=response)
        yield login_request

    def _verify_login(self,response):
        try:
            username = response.xpath("//table[@class='composer_header']//div[@class='composer']//li")[1].xpath(".//span//text()").extract_first()
            username = re.compile("\d+").findall(username)[0]
            if username == self.username:
                self.log("登陆成功")
                return True
            else:
                self.log("登陆失败",level=logging.ERROR)
                return False
        except:
            return False

    def verify_login(self,response):
        ''' 若没有登陆状态，则返回一个登陆的请求。否则，返回None '''
        login_status = self._verify_login(response=response) if "login" in response.url else True
        if login_status:
            return None
        else:
            return self._login(response=response)

    def parse_item(self,response):
        start_url = self.start_url
        write_item = WriteSignalItem()

        login_request = self.verify_login(response=response)
        if not login_request:
            yield login_request

        if "http://portal.chd.edu.cn/" == response.url:
            yield Request(start_url,callback=self.parse_item,dont_filter=True)

        # 如果request_list不为空，那么将进行request_list中的request放入队列进行爬取
        # 否则重复开始页面爬取，直到有新的文章。
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
            imgs = [response.urljoin(img_link) for img_link in img_links]
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
        if imgs:
            item["img"] = imgs
        else:
            item["img"] = []
        item["detail_time"] = creat_time
        item["article_url"] = response.url
        item["power"] = self.power

        item["index"] = response.meta.get("index")

        if imgs:
            for img in imgs:
                if "http" in img:
                    yield Request(img, callback=self.parse_img, dont_filter=True,
                                  meta={"type": "image", "article_url": response.url})

        yield item

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

    def _next_request(self,response,start_url):
        pageIndex = response.meta.get("pageIndex", 0) + 1
        next_url = "http://portal.chd.edu.cn/detach.portal?pageIndex={}&pageSize=&.pmn=view&.ia=false&action=bulletinsMoreView&search=true&groupid=all&.pen=pe65".format(
            pageIndex)

        # 用来判断是否要继续爬取
        info = response.xpath("//div[@class='pagination-info clearFix']//span//text()").extract_first()
        if info:
            info = re.compile("\d*/\d*").findall(info)[0]
            news_amount, page_amount = info.split("/")
            if int(page_amount) >= pageIndex:
                return Request(url=next_url, callback=self.parse_item,
                               meta={
                                   "type": "item",
                                   "start_url": start_url,
                                   "pageIndex":pageIndex
                               })
            else:
                self.log("信息门户爬取结束，爬取页数{}".format(pageIndex), level=logging.WARNING)
                return {"type":1,"index":0}

        else:
            self.log("没有找到文章数和页数，版块链接：%s" % response.url, level=logging.ERROR)
            return {"type": 1, "index": 0}

    def _article_requests(self,response):
        index = self.order
        request_list = []

        article_urls = response.xpath("//ul[@class='rss-container clearFix']//li//a[@class='rss-title']//@href").extract()
        for article_url in article_urls:
            article_url = response.urljoin(article_url)
            exist = self.filter.filter(article_url)
            if not exist:
                request = Request(article_url, callback=self.parse_article,
                                  meta={
                                      "type": "article",
                                      "index":index,
                                  })
                request_list.append(request)
                index += 1

        return request_list


