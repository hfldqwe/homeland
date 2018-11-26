import requests

response = requests.get("http://www.yiban.cn/forum/article/show/article_id/52241634/channel_id/70896/puid/5370552")
print(response.cookies)