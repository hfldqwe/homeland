# 易班HAPP抓包获取HTTP接口

## 登陆（一卡通登陆）

### chd登陆

**学校一卡通登陆，后面的参数是跳转的地址：**

```http request
http://ids.chd.edu.cn/authserver/login?service=http://ids.chddata.com/?mobile=1
```
**参数：**

GET请求：无参数，不需要cookies

POST请求：不需要cookies
```python
response = None # 不需要的一行

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
```

**结果：**

登陆之后会进行跳转，跳转到ids.chddata....页面，然后会接着跳转，会跳转到yiban的接口，获得一个**say**数据

获取say，为接下来获取access_token做准备
```python
response=None   # 无用的一行

say = response.xpath("//input//@value").extract_first()
```

### 获取yiban的access_token

**获取易班access_token**

```http request
https://o.yiban.cn/uiss/check?scid=10002_0&type=mobile
```

**参数：**

POST请求：不需要cookies，但是返回之后的cookies有用
```python
data = {
    "say":"之前获取到的say",
}
```

**结果：**

虽然返回了一个错误页面，但是其实是成功了的  

我们需要获取cookies中的**access_token**这个数据
```python
data = {
        "say":"............",
    }
response = requests.post(say_url,data=data,headers=headers) # 获取access_token
cookies = response.cookies
access_token = cookies["access_token"]
```

### 验证登陆是否成功，并且让易班登陆和学校联系起来

**让不进行这个请求，那么最终获取首页数据，会没有学校news的数据**
```http request
https://mobile.yiban.cn/api/v3/passport/autologin
```

**参数：**

GET请求：无cookies，有一个参数access_token

**结果：**

获取一个json数据，没有我们需要用到的数据，感觉这些数据更多是让服务器端知道，
把我们的access_token和学校的id关联起来
```json
```

### 获取易班新闻 ###

**请求学校新闻或者是易班平台首页数据**
```http request
https://mobile.yiban.cn/api/v3/home?access_token=f3e5799de50f4b486ee3bfded80dab18

https://mobile.yiban.cn/api/v3/home/news/school?access_token=f3e5799de50f4b486ee3bfded80dab18&page=4
```

**参数：**

GET请求：第一个链接，参数只有access_token的时候，是请求易班首页数据json
```python
data = {
    "title":"长安大学·易班",
    "user":{'id': 14411850, 'userName': '', 'avatar': 'http://img02.fs.yiban.cn/14411850/avatar/user/88?v=0'},
    "banner":[
            {'title': '易起过中秋', 'image': 'http://img01.fs.yiban.cn/pic/5370552/web/thumb_640x0/122429938.jpg', 'url': 'http://www.yiban.cn/forum/article/show/channel_id/70896/puid/5370552/article_id/46606894/group_id/0?access_token=f3e5799de50f4b486ee3bfded80dab18&v_time=154246592085805'},
            {'title': '易班纳新', 'image': 'http://img01.fs.yiban.cn/pic/5370552/web/thumb_640x0/125154069.jpg', 'url': 'http://cn.mikecrm.com/9L1zAMD'}, 
            {'title': '最红写手 非我莫属', 'url': 'http://proj.yiban.cn/project/yzxs/index.php?access_token=f3e5799de50f4b486ee3bfded80dab18&v_time=154246592039942', 'image': 'http://www.yiban.cn/upload/system/201811/181111172251666673.jpg'},
            {'title': '释放青春正能量', 'url': 'https://q.yiban.cn/app/index/appid/318260?access_token=f3e5799de50f4b486ee3bfded80dab18&v_time=154246592023543', 'image': 'http://www.yiban.cn/upload/system/201811/181109170456531532.jpg'}, {'title': '2018高校易班原创应用和特色项目招募令', 'url': 'https://q.yiban.cn/app/index/appid/310950?access_token=f3e5799de50f4b486ee3bfded80dab18&v_time=154246592092163', 'image': 'http://www.yiban.cn/upload/system/201811/181109135657682327.jpg'}, {'title': '共筑青春鸿鹄志 “易”起说说心里话', 'url': 'https://q.yiban.cn/app/index/appid/283782?access_token=f3e5799de50f4b486ee3bfded80dab18&v_time=154246592047806', 'image': 'http://www.yiban.cn/upload/system/201810/181029162746346077.jpg'}, {'title': '说说改革开放四十年', 'url': 'https://q.yiban.cn/app/index/appid/266242?access_token=f3e5799de50f4b486ee3bfded80dab18&v_time=154246592034197', 'image': 'http://www.yiban.cn/upload/system/201808/180821155322583695.jpg'}, {'title': '着我汉服衣裳，兴我礼仪之邦', 'url': 'https://q.yiban.cn/app/index/appid/310472?access_token=f3e5799de50f4b486ee3bfded80dab18&v_time=154246592045433', 'image': 'http://www.yiban.cn/upload/system/201810/181031113026445412.jpg'}
        ],
    "coming":None,
    "checkin":{'activity': None, 'normal': {'title': '普通签到', 'intro': '今天你签到了吗~签到后可以随机获得奖励哦~~'}},
    "hotApps":[
            {'name': '易瞄瞄', 'url': 'http://www.yiban.cn/mobile/index.html', 'hyaline': False, 'icon': 'http://www.yiban.cn/upload/system/201711/171117175137168235.png'}, 
            {'url': 'yiban://apps/99?userId=14653438', 'hyaline': False, 'name': '陕西省高校易班发展中心', 'icon': 'http://img02.fs.yiban.cn/14653438/avatar/user/68?v=0'}, 
            {'name': '易班熊', 'url': 'https://pet.yiban.cn?access_token=f3e5799de50f4b486ee3bfded80dab18&v_time=154246592024223', 'hyaline': False, 'icon': 'http://www.yiban.cn/upload/system/201805/180522180441332330.png'}, 
            {'name': '校园好声音', 'url': 'https://voice.yiban.cn?access_token=f3e5799de50f4b486ee3bfded80dab18&v_time=154246592094768', 'hyaline': False, 'icon': 'http://www.yiban.cn/upload/system/201809/180913192957998373.png'}, {'name': '校方认证', 'url': 'http://mobile.yiban.cn/api/passport/schoolcert?access_token=f3e5799de50f4b486ee3bfded80dab18&v_time=154246592055812', 'hyaline': False, 'icon': 'http://www.yiban.cn/upload/system/201606/160628164738937223.png'}, {'name': '精品课程', 'url': 'https://www.yooc.me/mobile?redirect=courses&access_token=f3e5799de50f4b486ee3bfded80dab18&v_time=154246592029504', 'hyaline': False, 'icon': 'http://www.yiban.cn/upload/system/201606/160624101607521961.png'}, {'name': '能力测评', 'url': 'https://f.yiban.cn/iapp198861?access_token=f3e5799de50f4b486ee3bfded80dab18&v_time=154246592035942', 'hyaline': False, 'icon': 'http://www.yiban.cn/upload/system/201808/180801173002668695.jpg'}, {'name': '金牌榜单', 'url': 'http://www.yiban.cn/mobile/medal/?access_token=f3e5799de50f4b486ee3bfded80dab18&v_time=154246592052603', 'hyaline': False, 'icon': 'http://www.yiban.cn/upload/system/201506/150602175144578400.png'}, {'name': '应用广场', 'url': 'yiban://apps/1', 'hyaline': False, 'icon': 'http://www.yiban.cn/upload/system/201506/150602175731134491.png'}, {'name': '各类活动', 'url': 'yiban://apps/2', 'hyaline': False, 'icon': 'http://www.yiban.cn/upload/system/201506/150602175749490797.png'}, {'name': '聚焦话题', 'url': 'http://www.yiban.cn/Forum/Star/replyclick?access_token=f3e5799de50f4b486ee3bfded80dab18&v_time=154246592016031', 'hyaline': False, 'icon': 'http://www.yiban.cn/upload/system/201506/150609175509934335.png'}, {'name': '明星用户', 'url': 'http://www.yiban.cn/Forum/Star/index?access_token=f3e5799de50f4b486ee3bfded80dab18&v_time=154246592025880', 'hyaline': False, 'icon': 'http://www.yiban.cn/upload/system/201506/150602175850297518.png'}, {'name': '热门问卷', 'url': 'http://www.yiban.cn/questionnaire/index/mhot?access_token=f3e5799de50f4b486ee3bfded80dab18&v_time=154246592092685', 'hyaline': False, 'icon': 'http://www.yiban.cn/upload/system/201506/150602175902695469.png'}, {'name': '名家博客', 'url': 'http://www.yiban.cn/mobile/blog/?access_token=f3e5799de50f4b486ee3bfded80dab18&v_time=154246592091805', 'hyaline': False, 'icon': 'http://www.yiban.cn/upload/system/201506/150609091855514372.png'}, {'name': '热门资料', 'url': 'yiban://apps/3', 'hyaline': False, 'icon': 'http://www.yiban.cn/upload/system/201507/150710155247816063.png'}
        ],
    "news":{'tabs': [
                    {'name': '学校', 'apiUrl': 'http://mobile.yiban.cn/api/v3/home/news/school'}, 
                    {'name': '易班推荐', 'apiUrl': 'http://mobile.yiban.cn/api/v3/home/news/yiban'}
                ],
            'list': {
                    'head': {
                            'avatar': 'http://img02.fs.yiban.cn/5370552/avatar/user/88?v=0', 'name': '长安大学主页', 'id': 5370552, 'url': 'yiban://organizations/5370552?type=1'}, 
                    'data': [
                            {'title': '双十一，温暖送给“易”中人', 'summary': '11月11日，树蕙园广场，易班工作站“双十一，将温暖送给‘易’中人”活动顺利举行！同学们...', 'url': 'http://www.yiban.cn/forum/article/show/article_id/52544020/channel_id/70896/puid/5370552', 'images': ['http://yfs01.fs.yiban.cn/web/1WGRPV'], 'type': 2, 'fromIcon': 'http://mobile.yiban.cn/h5/upload/files/home_news_wsq_icon.jpg', 'from': '微社区', 'publishedAt': '3天前'}, 
                            {'title': '早起      让生活换个美丽的模样', 'summary': '如果坚持早起生活会不会换一个美丽的模样每天都在上演的三件事：晚上睡不着，早上起不...', 'url': 'http://www.yiban.cn/forum/article/show/article_id/52241634/channel_id/70896/puid/5370552', 'images': ['http://yfs01.fs.yiban.cn/web/1VA5Z1'], 'type': 2, 'fromIcon': 'http://mobile.yiban.cn/h5/upload/files/home_news_wsq_icon.jpg', 'from': '微社区', 'publishedAt': '3天前'}, 
                            {'title': '今天，你剁手了吗？', 'summary': '阿里速度，2018天猫双11成交额不到两小时破千亿，今天，你“剁手”了吗？从 ...', 'url': 'http://www.yiban.cn/forum/article/show/article_id/52241932/channel_id/70896/puid/5370552', 'images': ['http://yfs01.fs.yiban.cn/web/1W2F2L'], 'type': 2, 'fromIcon': 'http://mobile.yiban.cn/h5/upload/files/home_news_wsq_icon.jpg', 'from': '微社区', 'publishedAt': '3天前'}, 
                            {'title': '要期中考试了', 'summary': '要期中考试了不知不觉间，这一学期已过去一半，期中考试即将来临。面对即将到来的期中...', 'url': 'http://www.yiban.cn/forum/article/show/article_id/52227362/channel_id/70896/puid/5370552', 'images': ['http://yfs01.fs.yiban.cn/web/1W27WL'], 'type': 2, 'fromIcon': 'http://mobile.yiban.cn/h5/upload/files/home_news_wsq_icon.jpg', 'from': '微社区', 'publishedAt': '4天前'}, {'title': '毒液;致命守护者上映', 'summary': '《毒液:致命守护者》 将在11月9日在国内上映，蜘蛛侠最强劲敌“毒液”强势来袭！《毒液...', 'url': 'http://www.yiban.cn/forum/article/show/article_id/51477168/channel_id/70896/puid/5370552', 'images': ['http://yfs01.fs.yiban.cn/web/1VCL0N'], 'type': 2, 'fromIcon': 'http://mobile.yiban.cn/h5/upload/files/home_news_wsq_icon.jpg', 'from': '微社区', 'publishedAt': '1周前'}, {'title': '羽生结弦：我就是风暴', 'summary': '短节目2018年11月3日，花样滑冰大奖赛芬兰大赛，日本花滑选手羽生结弦以短节目106.69...', 'url': 'http://www.yiban.cn/forum/article/show/article_id/51126496/channel_id/70896/puid/5370552', 'images': ['http://yfs01.fs.yiban.cn/web/1VFEHH'], 'type': 2, 'fromIcon': 'http://mobile.yiban.cn/h5/upload/files/home_news_wsq_icon.jpg', 'from': '微社区', 'publishedAt': '1周前'}, {'title': '视觉设计组优秀作品展', 'summary': 'Attention！视觉设计组经过相关培训，同学们纷纷交出了优秀的答卷，接下来请欣赏他们...', 'url': 'http://www.yiban.cn/forum/article/show/article_id/51076060/channel_id/70896/puid/5370552', 'images': ['http://yfs01.fs.yiban.cn/web/1VH2T5'], 'type': 2, 'fromIcon': 'http://mobile.yiban.cn/h5/upload/files/home_news_wsq_icon.jpg', 'from': '微社区', 'publishedAt': '1周前'}, {'title': '技术组分享会 | 帮你理解vue', 'summary': '——技术组分享会第4期——前端框架vue的应用时间： 2018.11.4主讲人：李晨东技术组分享会...', 'url': 'http://www.yiban.cn/forum/article/show/article_id/50948364/channel_id/70896/puid/5370552', 'images': ['http://yfs01.fs.yiban.cn/web/1VESE7'], 'type': 2, 'fromIcon': 'http://mobile.yiban.cn/h5/upload/files/home_news_wsq_icon.jpg', 'from': '微社区', 'publishedAt': '1周前'}, {'title': '双十一来了', 'summary': '双十一的历史，现状，优缺点，规划', 'url': 'http://www.yiban.cn/forum/article/show/article_id/50883172/channel_id/70896/puid/5370552', 'images': ['http://yfs01.fs.yiban.cn/web/1VD5UT'], 'type': 2, 'fromIcon': 'http://mobile.yiban.cn/h5/upload/files/home_news_wsq_icon.jpg', 'from': '微社区', 'publishedAt': '1周前'}, {'title': '技术组分享会 | 前端框架vue的应用', 'summary': '— 技术组分享会第4期 —前端框架vue的应用时间：2018.11.4主讲人：李承东•\xa0主讲人介绍\xa0...', 'url': 'http://www.yiban.cn/forum/article/show/article_id/50681222/channel_id/70896/puid/5370552', 'images': ['http://yfs01.fs.yiban.cn/web/1V7XD9'], 'type': 3, 'fromIcon': 'http://mobile.yiban.cn/h5/upload/files/home_news_wsq_icon.jpg', 'from': '微社区', 'publishedAt': '1周前'}, {'title': '技术组分享会|Python开发基本介绍', 'summary': '-技术组分享会第3讲-Python开发基本介绍时间：2018.10.28（本周日晚7：00）主讲人：董...', 'url': 'http://www.yiban.cn/forum/article/show/article_id/49463558/channel_id/70896/puid/5370552', 'images': ['http://yfs01.fs.yiban.cn/web/1UB5BP'], 'type': 2, 'fromIcon': 'http://mobile.yiban.cn/h5/upload/files/home_news_wsq_icon.jpg', 'from': '微社区', 'publishedAt': '3周前'}, {'title': '桥连港珠澳，风满大湾区', 'summary': '2018年10月23日，港珠澳大桥开通仪式在珠海举行，习近平主席出席仪式。从2009年12月15...', 'url': 'http://www.yiban.cn/forum/article/show/article_id/48923092/channel_id/70896/puid/5370552', 'images': ['http://yfs01.fs.yiban.cn/web/1TUY8D'], 'type': 3, 'fromIcon': 'http://mobile.yiban.cn/h5/upload/files/home_news_wsq_icon.jpg', 'from': '微社区', 'publishedAt': '3周前'}, {'title': '技术组分享会 | 教你制作网上导航', 'summary': '——技术组分享会第二期——\xa0 \xa0 制作分类导航栏\xa0时间：2018.10.21主讲人：王洁琳10月21日....', 'url': 'http://www.yiban.cn/forum/article/show/article_id/48914660/channel_id/70896/puid/5370552', 'images': ['http://yfs01.fs.yiban.cn/web/1TE7GF'], 'type': 2, 'fromIcon': 'http://mobile.yiban.cn/h5/upload/files/home_news_wsq_icon.jpg', 'from': '微社区', 'publishedAt': '3周前'}, {'title': '技术组分享会 | 制作分类导航栏', 'summary': '— 技术组分享会第2讲\xa0 —web前端（用CSS和javasscript制作分类导航栏）时间：2018...', 'url': 'http://www.yiban.cn/forum/article/show/article_id/48403042/channel_id/70896/puid/5370552', 'images': ['http://yfs01.fs.yiban.cn/web/1TE7GF'], 'type': 2, 'fromIcon': 'http://mobile.yiban.cn/h5/upload/files/home_news_wsq_icon.jpg', 'from': '微社区', 'publishedAt': '4周前'}, {'title': '技术组分享会 | 爬虫技术与web开发', 'summary': '— 技术组分享会第1期 —爬虫技术与web开发时间：2018.10.14主讲人：刘涛技术组分享会第...', 'url': 'http://www.yiban.cn/forum/article/show/article_id/48174484/channel_id/70896/puid/5370552', 'images': ['http://yfs01.fs.yiban.cn/web/1SN4XR'], 'type': 2, 'fromIcon': 'http://mobile.yiban.cn/h5/upload/files/home_news_wsq_icon.jpg', 'from': '微社区', 'publishedAt': '4周前'}, {'title': '技术组分享会 | “爬虫”帮你看小说', 'summary': '— 技术组分享会第1讲 —爬虫技术与web开发时间：2018.10.14主讲人：刘涛•\xa0主讲人介绍\xa0•...', 'url': 'http://www.yiban.cn/forum/article/show/article_id/47645626/channel_id/70896/puid/5370552', 'images': ['http://yfs01.fs.yiban.cn/web/1SN4XR'], 'type': 2, 'fromIcon': 'http://mobile.yiban.cn/h5/upload/files/home_news_wsq_icon.jpg', 'from': '微社区', 'publishedAt': '1月前'}, {'title': '秋风得意，看尽长安花', 'summary': '\xa0 \xa0 \xa0 \xa0 \xa0 千年古都——西安西安，古称长安，京兆，是中国历史上建都朝代最多，时间最长...', 'url': 'http://www.yiban.cn/forum/article/show/article_id/47000170/channel_id/70896/puid/5370552', 'images': ['http://yfs01.fs.yiban.cn/web/1PTDID'], 'type': 2, 'fromIcon': 'http://mobile.yiban.cn/h5/upload/files/home_news_wsq_icon.jpg', 'from': '微社区', 'publishedAt': '1月前'}, {'title': '愿得年年，常见中秋月', 'summary': '中秋节，又称月夕，秋节，仲秋节，八月节，八月会，追月节，玩月节，拜月节，女儿节或...', 'url': 'http://www.yiban.cn/forum/article/show/article_id/46606894/channel_id/70896/puid/5370552', 'images': ['http://yfs01.fs.yiban.cn/web/1RGKGF'], 'type': 2, 'fromIcon': 'http://mobile.yiban.cn/h5/upload/files/home_news_wsq_icon.jpg', 'from': '微社区', 'publishedAt': '1月前'}, {'title': '九一八 | 我们从未忘记', 'summary': '八十七年前的今天，1931年9月18日，“九一八”事变爆发。之后十四年，大片国土沦陷，350...', 'url': 'http://www.yiban.cn/forum/article/show/article_id/46350436/channel_id/70896/puid/5370552', 'images': ['http://yfs01.fs.yiban.cn/web/1R4C1F'], 'type': 2, 'fromIcon': 'http://mobile.yiban.cn/h5/upload/files/home_news_wsq_icon.jpg', 'from': '微社区', 'publishedAt': '1月前'}, {'title': '我们为什么要加入共青团？', 'summary': '我们到底为什么要加入共青团？经常有同学很迷惑', 'url': 'http://www.yiban.cn/forum/article/show/channel_id/70896/puid/5370552/article_id/44881620/', 'images': ['http://yfs01.fs.yiban.cn/web/1NV4M7'], 'type': 2, 'fromIcon': 'http://mobile.yiban.cn/h5/upload/files/6920fdc01c347cc055fa7c47629cbdf6.jpeg', 'from': '资讯', 'publishedAt': '4月前'}
                        ], 
                    'pagination': {
                            'perPage': 10, 
                            'currentPage': 1, 
                            'nextPageUrl': 'https://mobile.yiban.cn/api/v3/home/news/school?page=2',
                            'prevPageUrl': None, 
                            'from': 0, 
                            'to': 19}}
            }

}
```
GET请求，第二个链接，参数有access_token，和page的时候

```python
{
"data":
    {'list': {
        'head': {
            'avatar': 'http://img02.fs.yiban.cn/5370552/avatar/user/88?v=0', 'name': '长安大学主页', 'id': 5370552, 'url': 'yiban://organizations/5370552?type=1'}, 
        'data': [
                {'title': '双十一，温暖送给“易”中人', 'summary': '11月11日，树蕙园广场，易班工作站“双十一，将温暖送给‘易’中人”活动顺利举行！同学们...', 'url': 'http://www.yiban.cn/forum/article/show/article_id/52544020/channel_id/70896/puid/5370552', 'images': ['http://yfs01.fs.yiban.cn/web/1WGRPV'], 'type': 2, 'fromIcon': 'http://mobile.yiban.cn/h5/upload/files/home_news_wsq_icon.jpg', 'from': '微社区', 'publishedAt': '3天前'}, 
                {'title': '早起      让生活换个美丽的模样', 'summary': '如果坚持早起生活会不会换一个美丽的模样每天都在上演的三件事：晚上睡不着，早上起不...', 'url': 'http://www.yiban.cn/forum/article/show/article_id/52241634/channel_id/70896/puid/5370552', 'images': ['http://yfs01.fs.yiban.cn/web/1VA5Z1'], 'type': 2, 'fromIcon': 'http://mobile.yiban.cn/h5/upload/files/home_news_wsq_icon.jpg', 'from': '微社区', 'publishedAt': '3天前'}, 
                {'title': '今天，你剁手了吗？', 'summary': '阿里速度，2018天猫双11成交额不到两小时破千亿，今天，你“剁手”了吗？从 ...', 'url': 'http://www.yiban.cn/forum/article/show/article_id/52241932/channel_id/70896/puid/5370552', 'images': ['http://yfs01.fs.yiban.cn/web/1W2F2L'], 'type': 2, 'fromIcon': 'http://mobile.yiban.cn/h5/upload/files/home_news_wsq_icon.jpg', 'from': '微社区', 'publishedAt': '3天前'}, 
                {'title': '要期中考试了', 'summary': '要期中考试了不知不觉间，这一学期已过去一半，期中考试即将来临。面对即将到来的期中...', 'url': 'http://www.yiban.cn/forum/article/show/article_id/52227362/channel_id/70896/puid/5370552', 'images': ['http://yfs01.fs.yiban.cn/web/1W27WL'], 'type': 2, 'fromIcon': 'http://mobile.yiban.cn/h5/upload/files/home_news_wsq_icon.jpg', 'from': '微社区', 'publishedAt': '4天前'}, {'title': '毒液;致命守护者上映', 'summary': '《毒液:致命守护者》 将在11月9日在国内上映，蜘蛛侠最强劲敌“毒液”强势来袭！《毒液...', 'url': 'http://www.yiban.cn/forum/article/show/article_id/51477168/channel_id/70896/puid/5370552', 'images': ['http://yfs01.fs.yiban.cn/web/1VCL0N'], 'type': 2, 'fromIcon': 'http://mobile.yiban.cn/h5/upload/files/home_news_wsq_icon.jpg', 'from': '微社区', 'publishedAt': '1周前'}, {'title': '羽生结弦：我就是风暴', 'summary': '短节目2018年11月3日，花样滑冰大奖赛芬兰大赛，日本花滑选手羽生结弦以短节目106.69...', 'url': 'http://www.yiban.cn/forum/article/show/article_id/51126496/channel_id/70896/puid/5370552', 'images': ['http://yfs01.fs.yiban.cn/web/1VFEHH'], 'type': 2, 'fromIcon': 'http://mobile.yiban.cn/h5/upload/files/home_news_wsq_icon.jpg', 'from': '微社区', 'publishedAt': '1周前'}, {'title': '视觉设计组优秀作品展', 'summary': 'Attention！视觉设计组经过相关培训，同学们纷纷交出了优秀的答卷，接下来请欣赏他们...', 'url': 'http://www.yiban.cn/forum/article/show/article_id/51076060/channel_id/70896/puid/5370552', 'images': ['http://yfs01.fs.yiban.cn/web/1VH2T5'], 'type': 2, 'fromIcon': 'http://mobile.yiban.cn/h5/upload/files/home_news_wsq_icon.jpg', 'from': '微社区', 'publishedAt': '1周前'}, {'title': '技术组分享会 | 帮你理解vue', 'summary': '——技术组分享会第4期——前端框架vue的应用时间： 2018.11.4主讲人：李晨东技术组分享会...', 'url': 'http://www.yiban.cn/forum/article/show/article_id/50948364/channel_id/70896/puid/5370552', 'images': ['http://yfs01.fs.yiban.cn/web/1VESE7'], 'type': 2, 'fromIcon': 'http://mobile.yiban.cn/h5/upload/files/home_news_wsq_icon.jpg', 'from': '微社区', 'publishedAt': '1周前'}, {'title': '双十一来了', 'summary': '双十一的历史，现状，优缺点，规划', 'url': 'http://www.yiban.cn/forum/article/show/article_id/50883172/channel_id/70896/puid/5370552', 'images': ['http://yfs01.fs.yiban.cn/web/1VD5UT'], 'type': 2, 'fromIcon': 'http://mobile.yiban.cn/h5/upload/files/home_news_wsq_icon.jpg', 'from': '微社区', 'publishedAt': '1周前'}, {'title': '技术组分享会 | 前端框架vue的应用', 'summary': '— 技术组分享会第4期 —前端框架vue的应用时间：2018.11.4主讲人：李承东•\xa0主讲人介绍\xa0...', 'url': 'http://www.yiban.cn/forum/article/show/article_id/50681222/channel_id/70896/puid/5370552', 'images': ['http://yfs01.fs.yiban.cn/web/1V7XD9'], 'type': 3, 'fromIcon': 'http://mobile.yiban.cn/h5/upload/files/home_news_wsq_icon.jpg', 'from': '微社区', 'publishedAt': '1周前'}, {'title': '技术组分享会|Python开发基本介绍', 'summary': '-技术组分享会第3讲-Python开发基本介绍时间：2018.10.28（本周日晚7：00）主讲人：董...', 'url': 'http://www.yiban.cn/forum/article/show/article_id/49463558/channel_id/70896/puid/5370552', 'images': ['http://yfs01.fs.yiban.cn/web/1UB5BP'], 'type': 2, 'fromIcon': 'http://mobile.yiban.cn/h5/upload/files/home_news_wsq_icon.jpg', 'from': '微社区', 'publishedAt': '3周前'}, {'title': '桥连港珠澳，风满大湾区', 'summary': '2018年10月23日，港珠澳大桥开通仪式在珠海举行，习近平主席出席仪式。从2009年12月15...', 'url': 'http://www.yiban.cn/forum/article/show/article_id/48923092/channel_id/70896/puid/5370552', 'images': ['http://yfs01.fs.yiban.cn/web/1TUY8D'], 'type': 3, 'fromIcon': 'http://mobile.yiban.cn/h5/upload/files/home_news_wsq_icon.jpg', 'from': '微社区', 'publishedAt': '3周前'}, {'title': '技术组分享会 | 教你制作网上导航', 'summary': '——技术组分享会第二期——\xa0 \xa0 制作分类导航栏\xa0时间：2018.10.21主讲人：王洁琳10月21日....', 'url': 'http://www.yiban.cn/forum/article/show/article_id/48914660/channel_id/70896/puid/5370552', 'images': ['http://yfs01.fs.yiban.cn/web/1TE7GF'], 'type': 2, 'fromIcon': 'http://mobile.yiban.cn/h5/upload/files/home_news_wsq_icon.jpg', 'from': '微社区', 'publishedAt': '3周前'}, {'title': '技术组分享会 | 制作分类导航栏', 'summary': '— 技术组分享会第2讲\xa0 —web前端（用CSS和javasscript制作分类导航栏）时间：2018...', 'url': 'http://www.yiban.cn/forum/article/show/article_id/48403042/channel_id/70896/puid/5370552', 'images': ['http://yfs01.fs.yiban.cn/web/1TE7GF'], 'type': 2, 'fromIcon': 'http://mobile.yiban.cn/h5/upload/files/home_news_wsq_icon.jpg', 'from': '微社区', 'publishedAt': '4周前'}, {'title': '技术组分享会 | 爬虫技术与web开发', 'summary': '— 技术组分享会第1期 —爬虫技术与web开发时间：2018.10.14主讲人：刘涛技术组分享会第...', 'url': 'http://www.yiban.cn/forum/article/show/article_id/48174484/channel_id/70896/puid/5370552', 'images': ['http://yfs01.fs.yiban.cn/web/1SN4XR'], 'type': 2, 'fromIcon': 'http://mobile.yiban.cn/h5/upload/files/home_news_wsq_icon.jpg', 'from': '微社区', 'publishedAt': '4周前'}, {'title': '技术组分享会 | “爬虫”帮你看小说', 'summary': '— 技术组分享会第1讲 —爬虫技术与web开发时间：2018.10.14主讲人：刘涛•\xa0主讲人介绍\xa0•...', 'url': 'http://www.yiban.cn/forum/article/show/article_id/47645626/channel_id/70896/puid/5370552', 'images': ['http://yfs01.fs.yiban.cn/web/1SN4XR'], 'type': 2, 'fromIcon': 'http://mobile.yiban.cn/h5/upload/files/home_news_wsq_icon.jpg', 'from': '微社区', 'publishedAt': '1月前'}, {'title': '秋风得意，看尽长安花', 'summary': '\xa0 \xa0 \xa0 \xa0 \xa0 千年古都——西安西安，古称长安，京兆，是中国历史上建都朝代最多，时间最长...', 'url': 'http://www.yiban.cn/forum/article/show/article_id/47000170/channel_id/70896/puid/5370552', 'images': ['http://yfs01.fs.yiban.cn/web/1PTDID'], 'type': 2, 'fromIcon': 'http://mobile.yiban.cn/h5/upload/files/home_news_wsq_icon.jpg', 'from': '微社区', 'publishedAt': '1月前'}, {'title': '愿得年年，常见中秋月', 'summary': '中秋节，又称月夕，秋节，仲秋节，八月节，八月会，追月节，玩月节，拜月节，女儿节或...', 'url': 'http://www.yiban.cn/forum/article/show/article_id/46606894/channel_id/70896/puid/5370552', 'images': ['http://yfs01.fs.yiban.cn/web/1RGKGF'], 'type': 2, 'fromIcon': 'http://mobile.yiban.cn/h5/upload/files/home_news_wsq_icon.jpg', 'from': '微社区', 'publishedAt': '1月前'}, {'title': '九一八 | 我们从未忘记', 'summary': '八十七年前的今天，1931年9月18日，“九一八”事变爆发。之后十四年，大片国土沦陷，350...', 'url': 'http://www.yiban.cn/forum/article/show/article_id/46350436/channel_id/70896/puid/5370552', 'images': ['http://yfs01.fs.yiban.cn/web/1R4C1F'], 'type': 2, 'fromIcon': 'http://mobile.yiban.cn/h5/upload/files/home_news_wsq_icon.jpg', 'from': '微社区', 'publishedAt': '1月前'}, {'title': '我们为什么要加入共青团？', 'summary': '我们到底为什么要加入共青团？经常有同学很迷惑', 'url': 'http://www.yiban.cn/forum/article/show/channel_id/70896/puid/5370552/article_id/44881620/', 'images': ['http://yfs01.fs.yiban.cn/web/1NV4M7'], 'type': 2, 'fromIcon': 'http://mobile.yiban.cn/h5/upload/files/6920fdc01c347cc055fa7c47629cbdf6.jpeg', 'from': '资讯', 'publishedAt': '4月前'}
            ], 
        'pagination': {
                'perPage': 10, 
                'currentPage': 1, 
                'nextPageUrl': 'https://mobile.yiban.cn/api/v3/home/news/school?page=2',
                'prevPageUrl': None, 
                'from': 0, 
                'to': 19}},
},
    "message":"请求成功",
    "response":"100",
}
```

### 请求新闻地址，获取cookies ###
**请求地址**
```http request
http://www.yiban.cn/forum/article/show/article_id/52241634/channel_id/70896/puid/5370552

http://www.yiban.cn/forum/article/show/article_id/45810426/channel_id/70896/puid/5370552

```

**获取具体文章内容等参数**

```http request
http://www.yiban.cn/forum/article/showAjax
```

**参数**

POST请求：
```python
data = {
    "channel_id":"70896",
    "puid":"5370552",
    "article_id":"52544020",
    "origin":"0",
}
```

**结果：**
```json
{code: 200, message: "操作成功",…}
code
:
200
data
:
{urlParams: {channel_id: "70896", puid: 5370552}, baseUri: "/", jsBaseUrl: "/public/js/",…}
SectionFlag
:
1
article
:
{id: "52241634", Channel_id: "70896", User_id: "5370552", title: "早起 让生活换个美丽的模样", isNotice: "0",…}
Channel_id
:
"70896"
Sections_id
:
"0"
Sections_name
:
"默认版块"
UserGroup_id
:
"0"
User_id
:
"5370552"
author
:
{id: "5370552", isPublic: "0", isOrganization: "1", isDeveloper: "1", isSchoolVerify: "1",…}
addr
:
null
androidHomeUrl
:
"javascript:void(window.demo.toHomePage(5370552,12))"
area
:
null
authority
:
"1"
authorname
:
"长安大学"
avatar
:
"http://img02.fs.yiban.cn/5370552/avatar/user/200"
birth
:
"0000-00-00"
group_id
:
null
homeUrl
:
"/school/index/puserid/5370552"
id
:
"5370552"
img
:
"0"
iosHomeUrl
:
"http://www.yiban.cn/5370552/homepage/3"
isDeveloper
:
"1"
isOrganization
:
"1"
isPublic
:
"0"
isSchoolVerify
:
"1"
kind
:
"8"
major
:
""
name
:
"长安大学"
nick
:
"长安大学"
qr-add
:
"YWRkOjUzNzA1NTI="
qr-index
:
"aW5kZXg6NTM3MDU1Mg=="
regTime
:
"2015-04-16 10:08:29"
sex
:
"M"
source
:
"大学"
token
:
"7ee20803d4eb8ba8bb8bdb9a4bc27bb5"
userName
:
null
clicks
:
30
content
:
"<section style="font-family:'微软雅黑';"><section><section style="background-repeat:repeat;background-position:left top;padding:10px;background-size:auto;background-image:url(&quot;http://image2.135editor.com/mmbiz/yqVAqoZvDibEKKdJRMZeiaDEwgdkTbYoGahYPmfT4WFdrOECMlvTb596dNs0jcmRm2XkAJTia6s1knnFzFG1NxGbw/0&quot;);box-sizing:border-box;"><section class="xmteditor" style="display:none;"></section><p style="text-align:center;"><strong><span style="color:#00B0F0;font-family:'楷体', KaiTi, '楷体_GB2312', SimKai;font-size:24px;">如果坚持早起</span></strong></p><p style="text-align:center;"><strong><span style="font-family:'楷体', KaiTi, '楷体_GB2312', SimKai;font-size:24px;color:#00B0F0;">生活会不会换一个美丽的模样</span></strong><span style="color:#7F7F7F;font-family:'楷体', KaiTi, '楷体_GB2312', SimKai;font-size:24px;"><br></span></p><p><br></p><p><span style="color:#7F7F7F;">每天都在上演的三件事：晚上睡不着，早上起不来，后悔昨天睡的太晚!</span></p><p><span style="margin:0px;padding:0px;max-width:100%;color:#7F7F7F;box-sizing:border-box !important;">听说假期又短又无聊，其实是因为自己睡的太多......</span></p><p><span style="margin:0px;padding:0px;max-width:100%;color:#7F7F7F;box-sizing:border-box !important;">那如果我坚持早起，生活会不会换一个美丽的模样?</span></p><p><br></p><p><strong style="margin:0px;padding:0px;max-width:100%;text-align:center;box-sizing:border-box !important;"><strong style="margin:0px;padding:0px;max-width:100%;box-sizing:border-box !important;"><span style="margin:0px;padding:0px;max-width:100%;color:#00B0F0;box-sizing:border-box !important;">1. 精神变好</span></strong></strong></p><p><span style="margin:0px;padding:0px;max-width:100%;color:#7F7F7F;box-sizing:border-box !important;">坚持早起就会早睡。晚间身体进行排毒和休养，第二天人就会充满活力，那么精神状态自然是很好的。如此良性循环，每一天的自己都是容光焕发。</span></p><p><br></p><p><img src="http://img01.fs.yiban.cn/out/thumb_550x0/aHR0cDovL3lmczAxLmZzLnlpYmFuLmNuL3dlYi8xVkE1WjE=" style="margin:0px;padding:0px;box-sizing:border-box !important;width:auto !important;visibility:visible !important;" alt="1VA5Z1"><br style="margin:0px;padding:0px;max-width:100%;box-sizing:border-box !important;"></p><p><br></p><p><strong style="margin:0px;padding:0px;max-width:100%;box-sizing:border-box !important;"><span style="margin:0px;padding:0px;max-width:100%;color:#00B0F0;box-sizing:border-box !important;">2. 时间变多</span></strong></p><p><span style="margin:0px;padding:0px;max-width:100%;color:#7F7F7F;box-sizing:border-box !important;">如果你比别人早起一小时，你的一天就会比别人多做很多事情。效率也要高得多!如果周末的你不睡懒觉，就可以早起跑步，看书，吃早餐。当你把自己的电量充满会发现仅仅过了半个早上，那你的周末就比别人更有意义。</span></p><p><br></p><p><strong style="margin:0px;padding:0px;max-width:100%;box-sizing:border-box !important;"><span style="margin:0px;padding:0px;max-width:100%;color:#00B0F0;box-sizing:border-box !important;">3. 告别黑眼圈</span></strong></p><p><span style="margin:0px;padding:0px;max-width:100%;color:#7F7F7F;box-sizing:border-box !important;">身体是最经不得熬夜的，如果长期早起早睡，新陈代谢都会变得顺畅，心脏好、肝好、胃好、皮肤好......那你的黑眼圈还会有机会拉低你的颜值吗?</span></p><p><br></p><p><img src="http://img01.fs.yiban.cn/out/thumb_550x0/aHR0cDovL3lmczAxLmZzLnlpYmFuLmNuL3dlYi8xVVREQjM=" style="margin:0px;padding:0px;border-width:0px;list-style:none;box-sizing:border-box !important;width:auto !important;visibility:visible !important;" alt="1UTDB3"></p><p><br></p><p><strong style="margin:0px;padding:0px;max-width:100%;box-sizing:border-box !important;"><span style="margin:0px;padding:0px;max-width:100%;color:#00B0F0;box-sizing:border-box !important;">4. 减肥</span></strong></p><p><span style="margin:0px;padding:0px;max-width:100%;color:#7F7F7F;box-sizing:border-box !important;">经常熬夜的人内分泌失调就会导致体重失控，边减肥边熬夜是不行的!</span></p><p><br></p><p><strong style="margin:0px;padding:0px;max-width:100%;box-sizing:border-box !important;"><span style="margin:0px;padding:0px;max-width:100%;color:#00B0F0;box-sizing:border-box !important;">5. 享用自己做的早餐</span></strong><br style="margin:0px;padding:0px;max-width:100%;box-sizing:border-box !important;"></p><p><span style="margin:0px;padding:0px;max-width:100%;color:#7F7F7F;box-sizing:border-box !important;">想吃什么就做什么!自己做的早餐一定比外面的干净和健康。挑选新鲜的食材，做自己想吃的早餐，不用再为了赶时间匆忙敷衍自己的胃。</span></p><p><br></p><p><img src="http://img01.fs.yiban.cn/out/thumb_550x0/aHR0cDovL3lmczAxLmZzLnlpYmFuLmNuL3dlYi8xVkE1WjM=" style="margin:0px;padding:0px;box-sizing:border-box !important;width:auto !important;visibility:visible !important;" alt="1VA5Z3"><br style="margin:0px;padding:0px;max-width:100%;box-sizing:border-box !important;"></p><p><br></p><p><strong style="margin:0px;padding:0px;max-width:100%;box-sizing:border-box !important;"><span style="margin:0px;padding:0px;max-width:100%;color:#00B0F0;box-sizing:border-box !important;">6. 不用挤公交，挤地铁</span></strong></p><p><span style="margin:0px;padding:0px;max-width:100%;color:#7F7F7F;box-sizing:border-box !important;">早起就能早出门，不用挤公交不用挤地铁，更不用堵车!</span></p><p><br></p><p><strong style="margin:0px;padding:0px;max-width:100%;box-sizing:border-box !important;"><span style="margin:0px;padding:0px;max-width:100%;color:#00B0F0;box-sizing:border-box !important;">7. 欣赏别人看不到的美景</span></strong></p><p><span style="margin:0px;padding:0px;max-width:100%;color:#7F7F7F;box-sizing:border-box !important;">你可能会看到初升的太阳把光芒洒在大地上;你可能会看见路旁的花花草草生机勃勃;你可能会看见世界都是清新的模样。</span></p><p><br></p><p><img src="http://img01.fs.yiban.cn/out/thumb_550x0/aHR0cDovL3lmczAxLmZzLnlpYmFuLmNuL3dlYi8xVVREQjU=" style="margin:0px;padding:0px;border-width:0px;list-style:none;box-sizing:border-box !important;width:auto !important;visibility:visible !important;" alt="1UTDB5"></p><p><br></p><p><strong style="margin:0px;padding:0px;max-width:100%;box-sizing:border-box !important;"><span style="margin:0px;padding:0px;max-width:100%;color:#00B0F0;box-sizing:border-box !important;">8. 缓解焦虑</span></strong></p><p><span style="margin:0px;padding:0px;max-width:100%;color:#7F7F7F;box-sizing:border-box !important;">时间变得充裕了，生活变得充实了，那怎么还会有多余时间用来焦虑呢?</span></p><p><br></p><p><strong style="margin:0px;padding:0px;max-width:100%;box-sizing:border-box !important;"><span style="margin:0px;padding:0px;max-width:100%;color:#00B0F0;box-sizing:border-box !important;">9. 充满幸福感</span></strong></p><p><span style="margin:0px;padding:0px;max-width:100%;color:#7F7F7F;box-sizing:border-box !important;">大家都还沉睡梦乡的时候，你已经在为梦中的幸福而真实地努力了!</span></p><p><br></p><p><img src="http://img01.fs.yiban.cn/out/thumb_550x0/aHR0cDovL3lmczAxLmZzLnlpYmFuLmNuL3dlYi8xVVREQjk=" style="margin:0px;padding:0px;border-width:0px;list-style:none;box-sizing:border-box !important;width:auto !important;visibility:visible !important;" alt="1UTDB9"></p><p><br></p><p><strong style="margin:0px;padding:0px;max-width:100%;box-sizing:border-box !important;"><span style="margin:0px;padding:0px;max-width:100%;color:#00B0F0;box-sizing:border-box !important;">10. 会为将来而奋斗</span></strong></p><p><span style="margin:0px;padding:0px;max-width:100%;color:#7F7F7F;box-sizing:border-box !important;">连早起都无法做到，你还想升职加薪、脱离单身吗?</span></p><p><br></p><p><strong style="margin:0px;padding:0px;max-width:100%;box-sizing:border-box !important;"><span style="margin:0px;padding:0px;max-width:100%;color:#00B0F0;box-sizing:border-box !important;">11. 再不用多余的进补</span></strong></p><p><span style="margin:0px;padding:0px;max-width:100%;color:#7F7F7F;box-sizing:border-box !important;">人生已经充满幸福感，自此以后再也不用多余的进补啦!</span></p><p><span style="margin:0px;padding:0px;max-width:100%;color:#7F7F7F;box-sizing:border-box !important;">如果不坚持早起，那你的每一天都这样：</span></p><p><br></p><p><img src="http://img01.fs.yiban.cn/out/thumb_550x0/aHR0cDovL3lmczAxLmZzLnlpYmFuLmNuL3dlYi8xVUc1QVA=" style="margin:0px;padding:0px;border-width:0px;list-style:none;box-sizing:border-box !important;width:auto !important;visibility:visible !important;" alt="1UG5AP"></p><p><br></p><p><span style="margin:0px;padding:0px;max-width:100%;color:#7F7F7F;box-sizing:border-box !important;">如果每晚都早点睡，每早都坚持早点起，那生活就会很美好了。</span></p><p><span style="margin:0px;padding:0px;max-width:100%;color:#7F7F7F;box-sizing:border-box !important;">若不想被时间推着走，若不想每天都邋遢到无精打采，那么就早一点起床，做你能做的事吧!早起规划你的时间，就是早一步规划你的将来，那么你的人生必定是另一番模样! 如果计划开始早期，起床后在大学生励志网微信互动社区中发帖签到，一个人总是容易懒惰，加入一个积极向上的环境让生活充满更多力量。欢迎更多的同学加入大学生励志网早期签到的队伍中。</span></p><p style="text-align:center;"><span style="margin:0px;padding:0px;max-width:100%;color:#7F7F7F;box-sizing:border-box !important;"><img src="http://img01.fs.yiban.cn/out/thumb_550x0/aHR0cDovL3lmczAxLmZzLnlpYmFuLmNuL3dlYi8xVkE4OVQ=" title="1541338064703336.jpg" alt="冯晓祥.jpg"></span></p></section></section></section><p style="text-align:center;"><br></p>"
createTime
:
"11-12 23:52"
delPermission
:
false
editLog
:
[]
editPermission
:
false
files
:
[]
hotScore
:
"494897.97"
id
:
"52241634"
isLocked
:
"0"
isManager
:
0
isNotice
:
"0"
isOrganization
:
"1"
isUp
:
0
isWeb
:
"1"
oldAreaId
:
"0"
oldArtId
:
"0"
replyCount
:
"0"
replyTime
:
"11-12 23:52"
status
:
"1"
title
:
"早起      让生活换个美丽的模样"
upCount
:
"0"
updateTime
:
"11-12 23:52"
baseUri
:
"/"
channel_id
:
"70896"
cssBaseUrl
:
"/public/css/"
cssVersion
:
"201809201255"
currentUser
:
{avatar: "http://img02.fs.yiban.cn//avatar/user/200"}
avatar
:
"http://img02.fs.yiban.cn//avatar/user/200"
imgBaseUrl
:
"/public/images/"
isManager
:
0
isOrganization
:
"1"
jsBaseUrl
:
"/public/js/"
jsVersion
:
"201811091449"
puid
:
5370552
urlParams
:
{channel_id: "70896", puid: 5370552}
channel_id
:
"70896"
puid
:
5370552
message
:
"操作成功"
```


