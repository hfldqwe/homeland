# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import time
import os.path
from .models.news_model import YibanModel
from .models.filter_url import FilterUrl
import logging

from .spiders.info_spider import InfoSpider
from .spiders.xfjy_spider import XfjySpider
from .spiders.official_spider import OfficialSpider
from .spiders.yiban_spider import YibanSpider

from .utils.img_qiniu import UploadImage

from scrapy.exceptions import CloseSpider

from .items import ImageItem,WriteSignalItem

from scrapy import signals


logger = logging.getLogger()

class OrderPipeline:
    def __init__(self,*args,**kwargs):
        '''
        self.item_shelter = {<type1>:
                                    {
                                    1:item1,
                                    2:item2,
                                    ...
                                    },
                                ...
                                }
        self.item_scheduler = {<type1>:<order>,...}
        '''
        self.item_scheduler = {}    # 用于维护顺序
        self.item_shelter = {}      # 用于临时存储shelter

    def _add_shelter(self,item,type,index):
        ''' 增加item '''
        if type in self.item_shelter:
            self.item_shelter[type][index] = item
        else:
            self.item_shelter[type] = {"1":item}

    def _index_items(self,index,type,item,*args,**kwargs):
        if index == "0":
            index_items = self.item_shelter.pop(type)
            index_items = sorted(index_items.items(),reverse=True)
            return index_items
        else:
            return None

    def process_item(self, item, spider):
        index = item.get("index",1)
        type = item.get("type",None)
        if not type:
            logger.error("没有type，item：{}".format(item))
            return None

        index_items = self._index_items(index=index,type=type,item=item)
        if index_items:
            return index_items
        else:
            self._add_shelter(item=item,type=type,index=index)
        return

class ImagePipeline:
    def open_spider(self, spider):
        self.url = 'http://yibancdn.ohao.ren/'
        self.upload = UploadImage()

    def process_item(self, item, spider):
        if isinstance(item, ImageItem):
            name = item.get("name")
            name = self.dispose_url(name)
            image = item.get("img")
            article_url = item.get("article_url")
            image_url = item.get("image_url")
            if image:
                self.upload_image(img=image,name=name)
            else:
                logger.error("没有解析到图片,文章地址：{}，图片地址：{}".format(article_url,image_url))
            return None
        elif isinstance(item,WriteSignalItem):
            return item
        else:
            imgs = item.get("img")
            content = item.get("content")

            if imgs:
                imgs_new = [os.path.join(self.url,self.dispose_url(img_url)) for img_url in imgs]
                img = imgs_new[0]
                for i in range(len(imgs)):
                    content = content.replace(imgs[i],imgs_new[i])
            else:
                img = ""

            item["img"] = img.replace("http","https")
            item["content"] = content
            return item

    def dispose_url(self,url):
        name = url.split("/")[-1]
        name_suffix = name.split("=")[-1]
        if not name_suffix:
            name_suffix = name.split("=")[-2]
        name = "weappnews/" + name_suffix
        return name

    def upload_image(self,img,name):
        return self.upload.uplode(image_content=img,name=name)

class HomelandPipeline:
    def open_spider(self,spider):
        self.logger = logging.getLogger()
        if isinstance(spider,InfoSpider):
            self.source_type = spider.source_type
            if self.source_type == "info":
                name = "info_article_url"
            else:
                name = "infoteacher_article_url"
            self.channel_id = 7
        elif isinstance(spider,XfjySpider):
            name = "xfjy_article_url"
            self.source_type = "xfjy"
            self.channel_id = 5
        elif isinstance(spider,OfficialSpider):
            name = "official_article_url"
            self.source_type = "official"
            self.channel_id = 4
        elif isinstance(spider,YibanSpider):
            name = "yiban_article_url"
            self.source_type = "yiban"
            self.channel_id = 3
        else:
            self.logger.error("没有找到启动的爬虫,pipelines无法加载，%s" % spider.__class__)
            raise CloseSpider("没有找到启动的爬虫,pipelines无法加载，%s" % spider.__class__)

        self.yiban = YibanModel()
        self.filter_url = FilterUrl(name)
        self.data = list()

    def process_item(self, item, spider):
        if isinstance(item,WriteSignalItem):
            self.write_items()
            return

        if not item:
            return None

        article_url = item.get("article_url")
        img = item.get('img', '')
        if img:
            style = 2
        else:
            style = 0

        power = item.get("power", "all")
        if not power:
            power = "all"

        kwargs_dict = {
            # 额外的参数
            'article_url' : article_url,

            # archives表
            'channel_id' : self.channel_id,
            'model_id' : 1,
            'title' : item["title"],
            'flag' : '',
            'image' : img,
            'attachfile' : item.get("attch_name_url", ''),
            'keywords' : '',
            'description' : '',
            'tags' : item.get('block_type'),
            'weigh' : 0,
            'views' : 0,
            'comments' : 0,
            'likes' : 0,
            'dislikes' : 0,
            'diyname' : '',
            'createtime' : item.get('detail_time'),
            'publishtime' : int(time.time()),
            'status' : 'normal',
            'power' : power,  # 'all'.'student','teacher',

            # addonnews表
            'content' : item.get("content"),
            'author' : item.get("author",""),
            'style' : style,

            # tags表
            'tags_list' : item.get('tags_list'),

            "index":item.get("index"),
        }
        self.data.append(kwargs_dict)

    def write_items(self):
        if self.data:
            data = sorted(self.data,key=lambda x:x["index"],reverse=True)
            for kwargs_dict in data:
                try:
                    kwargs_dict.pop("index")

                    article_url = kwargs_dict.get("article_url")

                    passed = self.yiban.insert_mysql(kwargs_dict=kwargs_dict)
                    if passed:
                        self.filter_url.add(article_url)
                        self.logger.debug("插入数据库成功")
                    else:
                        self.logger.error("url不在过滤池中，文章却保存到了数据库")
                    self.data.remove(kwargs_dict)
                except BaseException as e:
                    self.logger.error(str(e))
                    self.logger.error("数据库交互出现了错误")

    def close_spider(self,spider):
        self.write_items()
        return

