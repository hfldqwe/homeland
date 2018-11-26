# 用于测试易班登陆

import requests
import json
from requests import Session
from scrapy import Selector

headers = {
    "User-Agent":"Mozilla/5.0 (Linux; Android 7.0; PRA-AL00X Build/HONORPRA-AL00X; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/64.0.3282.137 Mobile Safari/537.36",
}

chd_ids = "http://ids.chd.edu.cn/authserver/login?service=http://ids.chddata.com/?mobile=1"

say_url = "https://o.yiban.cn/uiss/check?scid=10002_0&type=mobile" # 用于易班获取say,这个请求之后的cookies中含有access_token，虽然页面是失败的

# sucess_url = "http://mobile.yiban.cn/api/passport/loginsucess"  # 当提交了post请求之后，然后访问loginsucess页面 这个页面是无用的，不需要这个

verify_url = "https://mobile.yiban.cn/api/v3/passport/autologin" # 用于验证是否登录成功

yiban_login_url = "https://mobile.yiban.cn/api/v3/sport/step?stepCount=1"   # 使用access_token进行请求，login_token和access_toke是一样的，这是个post请求，不知道有什么用

index_url = "https://mobile.yiban.cn/api/v3/home" # 这个是获取首页基础数据，一个json数据   需要一个get请求加参数access_token=f3e5799de50f4b486ee3bfded80dab18

req = Session()

def parse_chd(response):
    lt = response.xpath("//input[@name='lt']//@value").extract_first()
    dllt = response.xpath("//input[@name='dllt']//@value").extract_first()
    execution = response.xpath("//input[@name='execution']//@value").extract_first()
    _eventId = response.xpath("//input[@name='_eventId']//@value").extract_first()
    rmShown = response.xpath("//input[@name='rmShown']//@value").extract_first()

    formdata = {
        "username": '2017905714',
        "password": '100818',
        "lt": lt,
        "dllt": dllt,
        "execution": execution,
        "_eventId": _eventId,
        "rmShown": rmShown,
        "captchaResponse":"",
    }

    return formdata

def login(formata):
    response = req.post(chd_ids,headers=headers,data=formdata)
    response = Selector(response)

    return get_say(response)

def get_say(response):
    ''' 用于chd登陆之后，再次进行post请求，提交易班服务器，提取出下一步需要的数据say '''
    data = {
        "say":response.xpath("//input//@value").extract_first(),
    }
    response = requests.post(say_url,data=data,headers=headers) # 获取access_token
    cookies = response.cookies
    access_token = cookies["access_token"]

    return access_token


def verify_login(access_token):
    params = {"access_token":access_token,}
    response = requests.get(verify_url,headers=headers,params=params)


def get_index_data(access_token):
    params = {"access_token": access_token, }
    response = requests.get(index_url,headers=headers,params=params)
    return response.json()

def article_login():
    cookies = {
        "Cookie":"_YB_OPEN_V2_0=_m9hEvhhjl0200M2",
        "visit_school":"10002",
        "access_token":"b602e2a3befaad1b8b1239be414f9ca1",
    }
    headers = {
        "logintoken":"b602e2a3befaad1b8b1239be414f9ca1",
        "User-Agent":"Mozilla/5.0 (Linux; Android 7.1.1; OPPO R11 Build/NMF26X; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/55.0.2883.91 Mobile Safari/537.36 yiban_android",
        "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "X-Requested-With":"com.yiban.app",
        "signature":"6+lubjt7CaEY9yBHMOJabGR64UEhexKC5Mpo6h+dQrnsqJRK7M0cb7rt4zdoDNgp+xzNiExnXTV4h97gIaMoUQ",
        "authorization":"Bearer b602e2a3befaad1b8b1239be414f9ca1",
        "Upgrade-Insecure-Requests":"1",
        "Host":"www.yiban.cn",
    }
    response = requests.get("http://www.yiban.cn/forum/article/show/article_id/52241634/channel_id/70896/puid/5370552",cookies=cookies,headers=headers,allow_redirects=False)
    print(response.text)
    print(response.json())


if __name__ == '__main__':
    response = req.get(chd_ids, headers=headers)
    response = Selector(response)
    formdata = parse_chd(response)

    access_token = login(formdata)

    verify_login(access_token=access_token)

    data = get_index_data(access_token)
    data = data["data"]
    print(data)
# if __name__ == '__main__':
#     article_login()





