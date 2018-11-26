from requests_html import HTMLSession
from scrapy import Selector
from scrapy.shell import inspect_response

from requests_html import AsyncHTMLSession

session = HTMLSession()


headers = {"User-Agent":"Mozilla/5.0 (Linux; Android 7.0; PRA-AL00X Build/HONORPRA-AL00X; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/64.0.3282.137 Mobile Safari/537.36",}
response = session.get("http://www.yiban.cn/forum/article/show/article_id/52544020/channel_id/70896/puid/5370552#main-comment-target",headers=headers)
result = response.html
# print(result.html)
print(result.render(sleep=1))
# print(result.html)
response = Selector(text=result.html)

content = response.xpath("//div[@class='detail-forum-text']").extract_first()
img = response.xpath("//div[@class='detail-forum-text']//img//@data-original").extract()
detail_time = response.xpath("//ul[@class='cf']//li//text()").extract()


# content = result.xpath("//div[@class='detail-forum-text']",first=True).html
# img = result.xpath("//div[@class='detail-forum-text']//img")
# detail_time = result.xpath("//ul[@class='cf']//li//text()")
#
# # print(content)
# print(img)
# print(detail_time)

