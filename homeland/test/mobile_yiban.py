import requests
import pymysql
import time
import re
from bs4 import BeautifulSoup
import datetime


UA = "Mozilla/5.0 (Linux; Android 7.0; PRA-AL00X Build/HONORPRA-AL00X; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/64.0.3282.137 Mobile Safari/537.36"
headers = {'User-Agent':UA}

def get_access_token():
    url = "http://ids.chddata.com/mobile_sim.php"
    say = requests.get(url).text
    post_data = {'say': say}
    login_url = "http://o.yiban.cn/uiss/check?scid=10002_0&type=mobile"
    response = requests.post(login_url, data=post_data, headers=headers).headers
    print(response)
    if 'Set-Cookie' in response.keys():
        access_token = re.findall('access_token=(.*?);', response['Set-Cookie'])[1]
    else:
        time.sleep(5)
    return access_token

def main(access_token):
    success_url = "http://mobile.yiban.cn/api/v3/passport/autologin?access_token=%s" % access_token
    res_data = requests.get(success_url,headers=headers).json()
    list_url = 'http://mobile.yiban.cn/api/v3/home?access_token=%s' % access_token
    res_message = requests.get(list_url, headers=headers).json()
    status = res_message['message']
    if status != "请求成功":
        print(res_message)
    else:
        print(1)

if __name__ == '__main__':
    for i in range(2000):
        access_token = get_access_token()
        main(access_token)
    




