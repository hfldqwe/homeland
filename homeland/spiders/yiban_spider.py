import scrapy
import json
import logging
import time
from requests_html import AsyncHTMLSession,HTMLSession
from scrapy import Selector
from scrapy.http import Request,FormRequest
from scrapy.http.cookies import CookieJar
from scrapy.loader import ItemLoader
from scrapy_splash import SplashRequest

from ..items import WriteSignalItem,YibanArticleItem,ImageItem
from ..models.filter_url import FilterUrl
from ..utils import tool

from scrapy.shell import inspect_response

cookiejar = CookieJar()
headers = {"User-Agent":"Mozilla/5.0 (Linux; Android 7.0; PRA-AL00X Build/HONORPRA-AL00X; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/64.0.3282.137 Mobile Safari/537.36",}

class YibanSpider(scrapy.Spider):
    name = "yiban"
    allowed_domains = ['chd.edu.cn', 'yiban.cn']

    custom_settings = {
        "CONCURRENT_REQUESTS": 32,
        "DOWNLOAD_DELAY": 0,
        "DEFAULT_REQUEST_HEADERS":{
            "User-Agent":"Mozilla/5.0 (Linux; Android 7.0; PRA-AL00X Build/HONORPRA-AL00X; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/64.0.3282.137 Mobile Safari/537.36",
        },
        "INCREMENT_CRAWL": False,
    }

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        increment = crawler.settings.get("INCREMENT_CRAWL", False)
        spider = super().from_crawler(crawler, increment=increment, *args, **kwargs)
        return spider

    def __init__(self,username,password,increment=False,*args,**kwargs):
        super(YibanSpider,self).__init__(*args,**kwargs)
        redis_name = "yiban_article_url"
        self.filter = FilterUrl(redis_name)
        self.username = username
        self.password = password
        self.increment = increment
        self.login_url = "http://ids.chd.edu.cn/authserver/login?service=http://ids.chddata.com/?mobile=1"
        self.get_token_url = "https://o.yiban.cn/uiss/check?scid=10002_0&type=mobile"
        self.yiban_login_url = "https://mobile.yiban.cn/api/v3/passport/autologin"
        self.index_url = "https://mobile.yiban.cn/api/v3/home"
        self.after_index_url = "https://mobile.yiban.cn/api/v3/feeds/untouched"
        self.item_url = "https://mobile.yiban.cn/api/v3/home/news/school"
        self.article_url = "http://www.yiban.cn/forum/article/showAjax"
        # self.article_url = "http://www.yiban.cn/forum/reply/listAjax"
        self.access_token = None
        self.order = 1   # 键是block_type，值为index
        self.cookie = 0

    def start_requests(self):
        yield Request(url=self.login_url, dont_filter=True, callback=self.login,
                      meta={"type": "start",
                            "start_url": self.login_url})

    def login(self,response):
        login_request = self._login(response=response)
        yield login_request

    def _login(self,response):
        lt = response.xpath("//input[@name='lt']//@value").extract_first()
        dllt = response.xpath("//input[@name='dllt']//@value").extract_first()
        execution = response.xpath("//input[@name='execution']//@value").extract_first()
        _eventId = response.xpath("//input[@name='_eventId']//@value").extract_first()
        rmShown = response.xpath("//input[@name='rmShown']//@value").extract_first()

        formdata = {
            "username": self.username,
            "password": self.password,
            "lt": lt,
            "dllt": dllt,
            "execution": execution,
            "_eventId": _eventId,
            "rmShown": rmShown,
            "captchaResponse": "",
        }
        return FormRequest(self.login_url,
                          formdata=formdata,
                          callback=self.get_token,dont_filter=True,
                          )

    def get_token(self,response):
        say = response.xpath("//input//@value").extract_first()
        formdata = {"say":say}
        yield FormRequest(self.get_token_url,formdata=formdata,callback=self.yiban_login,dont_filter=True)

    def yiban_login(self,response):
        cookies = response.headers.getlist("Set-Cookie")
        cookie = cookies[-1]
        key_values = cookie.decode().split(";")[0].split("=")
        if key_values[0] == "access_token" and key_values[1] != "deleted":
            self.access_token = key_values[1]
            yiban_login_url = self.yiban_login_url + "?" +"access_token={}".format(self.access_token)
            yield Request(yiban_login_url,callback=self.start_item,dont_filter=True)
        else:
            self.log("没有解析到access_token，cookies：{}".format(cookie))
            time.sleep(3)
            yield from self.start_requests()

    def start_item(self, response):
        item_url = tool.group_query(self.item_url, {"access_token": self.access_token, "page": 1})
        yield Request(url=item_url,callback=self.parse_item,dont_filter=True,
                          priority=-1,
                          meta={
                              "type": "start",
                              "start_url":item_url,
                              "page":2,
                          })

    def parse_item(self,response):
        start_url = tool.group_query(self.item_url,{"access_token":self.access_token,"page":1})
        write_item = WriteSignalItem()

        login_request = self.verify_login(response=response)
        if not login_request:
            yield login_request

        # 如果request_list不为空，那么将进行request_list中的request放入队列进行爬取
        # 否则重复开始页面爬取，直到有新的文章。
        request_list = self._article_requests(response)
        if not request_list and self.increment:
            self.log("增量爬取")

            write_item["write"] = True
            yield write_item
            yield self.start_item(response)
        else:
            print(request_list)
            for request in request_list:
                yield request

            self.order += len(request_list)

            yield self._next_request(response,start_url)

    def verify_login(self,response):
        return True

    def _article_requests(self,response):
        request_list = []
        index = self.order
        data = json.loads(response.body)["data"]["list"]["data"]
        index += len(data)

        for article in data:
            article_url = article["url"]
            title = article["title"]
            article_data = article_url.split("/")
            article_id,channel_id,puid = article_data[-5::2]
            formdata = {
                "channel_id": channel_id,
                "puid": puid,
                "article_id": article_id,
                "origin": '0',
            }
            request = FormRequest(self.article_url,callback=self.parse_article_ajax,dont_filter=True,
                                  formdata=formdata,
                                  meta={
                                        "type": "article",
                                        "index": index,
                                        "title":title,
                                        "article_url":article_url,
                                  },
                                  )
            request_list.append(request)
            index += 1
        return request_list

    def _next_request(self,response,start_url):
        page = response.meta.get("page",None)
        next_url = json.loads(response.body)["data"]["list"]["pagination"]["nextPageUrl"]
        if not page:
            self.log("yiban：response中没有page",level=logging.ERROR)
            item_url = tool.group_query(self.item_url, {"access_token": self.access_token, "page": 1})
            return Request(url=item_url, callback=self.parse_item, dont_filter=True,
                           priority=-1,
                           meta={
                               "type": "start",
                               "start_url": self.start_urls,
                               "page":2,
                           })

        if next_url:
            item_url = tool.group_query(self.item_url,{"access_token":self.access_token,"page":page})
            return Request(url=item_url,callback=self.parse_item,dont_filter=True,
                              priority=-1,
                              meta={
                                  "type": "item",
                                  "start_url":self.start_urls,
                                  "page":page+1,
                              })
        else:
            self.log("yiban爬虫结束,",level=logging.ERROR)

    def parse_article_ajax(self,response):
        try:
            article = json.loads(response.body)["data"]["article"]
        except BaseException as e:
            self.log(response.body.decode(),level=logging.DEBUG)
            self.log("解析json过程出现错误，没有article，链接：{},错误：{}".format(response.url,str(e)),level=logging.ERROR)
            self.log("{}".format(str(response.request.body)),level=logging.ERROR)
        else:
            loader = ItemLoader(item=YibanArticleItem(),response=response)
            article_url = response.meta.get("article_url")
            title = response.meta.get("title")
            tags_list = ["易班",]
            tags_list.append(article.get("Sections_name"))
            block_type = ",".join(tags_list)
            content = article.get("content")
            detail_time = article.get("createTime")

            # 易班的网站上面没有附件
            attchments = ""

            index = response.meta.get("index")

            loader.add_value("article_url", article_url)
            loader.add_value("title", title)
            loader.add_value("tags_list", tags_list)
            loader.add_value("block_type", block_type)
            loader.add_value("content", content)

            content_response = Selector(text=content)
            loader.add_value("img", content_response.xpath("//img//@src").extract())
            loader.add_value("detail_time",detail_time)
            loader.add_value("index", index)

            imgs = loader.get_collected_values("img")
            if imgs:
                for img in imgs:
                    if "http" in img:
                        yield Request(img, callback=self.parse_img, dont_filter=True,
                                      meta={"type": "image", "article_url": article_url})
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