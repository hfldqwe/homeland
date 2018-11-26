import requests

def article():
    headers = {
        "User-Agent":"Mozilla/5.0 (Linux; Android 7.1.1; OPPO R11 Build/NMF26X; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/55.0.2883.91 Mobile Safari/537.36 yiban_android",
    }

    # cookies = {
    #     "_YB_OPEN_V2_0":"_m9hEvhhjl0200M2",
    #     "visit_school":"10002",
    #     "access_token":"b602e2a3befaad1b8b1239be414f9ca1",
    #     "YB_SSID":"f52006a616a3d991d380b0d1f182abcf",
    #     "yiban_user_token":"47e7dfa938505513e4c63cb33ff51ef7",
    # }

    data = {
        "channel_id":"70896",
        "puid":"5370552",
        "article_id":"53764466",
        "origin":"0",
    }

    response = requests.post("http://www.yiban.cn/forum/article/showAjax",data=data)
    print(response.text)
    print(response.json())

def article_login():
    headers = {
        "User-Agent":"Mozilla/5.0 (Linux; Android 7.1.1; OPPO R11 Build/NMF26X; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/55.0.2883.91 Mobile Safari/537.36 yiban_android",
        "Host":"www.yiban.cn",
        "logintoken":"b602e2a3befaad1b8b1239be414f9ca1",
    }
    cookies = {
        "_YB_OPEN_V2_0": "_m9hEvhhjl0200M2",
        "visit_school": "10002",
        "access_token": "b602e2a3befaad1b8b1239be414f9ca1",
    }

    response = requests.get("http://www.yiban.cn/forum/article/show/article_id/47645626/channel_id/70896/puid/5370552",headers=headers,cookies=cookies)

    print(response.text)
    print(response.json())


if __name__ == '__main__':
    article()