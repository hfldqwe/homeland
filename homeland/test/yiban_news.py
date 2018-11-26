import requests
import pymysql
import time
import re
from bs4 import BeautifulSoup
import datetime


UA = "Mozilla/5.0 (Linux; Android 7.0; PRA-AL00X Build/HONORPRA-AL00X; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/64.0.3282.137 Mobile Safari/537.36"
headers = {'User-Agent':UA}

def get_token():
    url = "http://mobile.yiban.cn/api/v2/passport/login?account=15690620473&passwd=nuli08111314&ct=2&app=1&v=4.5.7&apn=wifi&identify=865411030733078&sig=b6710c08f5259dfc&token=&device=HUAWEI%3APRA-AL00X&sversion=24"
    data = requests.get(url).json()
    if data['message'] == "请求成功":
        access_token = data['data']['access_token']
        print(access_token)
    return access_token


def get_data(access_token, url, type_site):
    params = {'access_token': access_token}
    data = requests.get(url, params=params).json()
    if data['message'] == "请求成功":
        news_data = data['data']['list']['data']
        for news in news_data:
            insert_data(news, type_site)

                

# 插入数据库
def insert_data(news, type_site):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'}
    title = news['title']
    image = news['images']
    if image:
        image = news['images'][0]
    else:
        image = ''
    url = news['url']
    element = re.findall('article_id/(\d+)/channel_id/(\d+)/puid/(\d+)', url)[0]
    article_id = element[0]
    channel_id = element[1]
    puid = element[2]
    post_data = {
        'channel_id': channel_id,
        'puid': puid,
        'article_id': article_id,
        'page': '1',
        'size': '5',
        'order': '1'
    }
    post_url = "http://www.yiban.cn/forum/reply/listAjax"
    response = requests.post(post_url, data=post_data, headers=headers).json()
    article_msg = response['data']['list']['article']
    content = article_msg['content']
    create_time = article_msg['createTime']
    #转换成时间数组
    timeArray = time.strptime(create_time, "%Y-%m-%d %H:%M:%S")
    #转换成时间戳
    create_time = int(time.mktime(timeArray))
    info = [title, create_time, content, image]
    insert_database(info, type_site)


def insert_database(info, type_site):
    # 连接数据库
    #conn = pymysql.connect(host='localhost', user='root', passwd='nuli08111314', db='fastadmin', charset='utf8') #db：库名
    conn = pymysql.connect(host='47.52.34.62', user='fastadmin' ,passwd='QuOwQ0T7XZRiPpd2', db='fastadmin', charset='utf8',port=3306) #db：库名
    # 创建游标
    cur = conn.cursor()
    # 设置游标类型，默认游标类型为元组形式
    # 将游标类型设置为字典形式
    cur = conn.cursor(cursor=pymysql.cursors.DictCursor)
    # 构造插入的数据
    channel_id = '3'
    block_type = type_site
    title = info[0]
    create_time = info[1]
    content = info[2]
    image = info[3]
    if(image):
        style = "2"
    else:
        style = "0"
    res = cur.execute('SELECT * FROM fa_cms_archives WHERE title = %s AND channel_id = %s ',(title, channel_id))
    if(res):
        print("重复")
    else:
        recount = cur.execute('insert into fa_cms_addonnews(content, style) values(%s, %s)', (content, style))
        rescount = cur.execute('insert into fa_cms_archives(channel_id, model_id, title, image, tags,createtime) values(%s, %s, %s, %s, %s, %s)', (channel_id, '1', title, image, block_type,create_time))
        last_id = int(conn.insert_id())
        if block_type == "易班校园":
            cur.execute('SELECT * FROM fa_cms_tags WHERE id = 58')
            article = cur.fetchone()
            archives = article['archives']
            nums = article['nums'] + 1
            archives = archives + str(last_id) + ","
            cur.execute('update fa_cms_tags set archives = %s, nums = %s  where id = 58',(archives, nums))
        elif block_type == "易班推荐":
            cur.execute('SELECT * FROM fa_cms_tags WHERE id = 59')
            article = cur.fetchone()
            archives = article['archives']
            nums = article['nums'] + 1
            archives = archives + str(last_id) + ","
            cur.execute('update fa_cms_tags set archives = %s, nums = %s where id = 59',(archives, nums))
        print(recount)
    # 提交
    conn.commit()
    # 关闭指针对象
    cur.close()
    # 关闭连接对象
    conn.close()

def main(name, url):
    access_token = get_token()
    # access_token = '567e54de6869824ef68f102128f0fd7d'
    get_data(access_token, url, name)

if __name__ == '__main__':
    url_school = "http://mobile.yiban.cn/api/v3/home/news/school"
    main("易班校园", url_school)
    # for i in range(2, 5):
    #     url_school_page = "http://mobile.yiban.cn/api/v3/home/news/school?page=%d" % i
    #     main("易班校园", url_school_page)
    #     time.sleep(2)

    # url_yiban = "http://mobile.yiban.cn/api/v3/home/news/yiban"
    # main("易班推荐", url_yiban)
