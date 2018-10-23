import pymysql
import logging
from configparser import ConfigParser


def mysql_conf(section):
    config = ConfigParser()
    config.read("/home/py/project/homeland/homeland/info.conf")
    if config.has_section(section):
        host = config.get(section, "host")
        port = config.getint(section, "port")
        username = config.get(section,"username")
        password = config.get(section, "password")
        db = config.get(section, "db")
        return host, port, username,password, db
    else:
        raise Exception("读取mysql配置出现错误")

class YibanModel():
    def __init__(self):
        host, port, username, password, db = mysql_conf("mysql_test")
        self.con = pymysql.connect(
            host = host,
            port = port,
            user = username,
            password = password,
            db = db,
        )
        self.cursor = self.con.cursor()
        self.logger = logging.getLogger()

    def filder_archives(self,article_url,title,publishtime,tags,*args,**kwargs):
        '''
        用来过滤掉重复的参数，判断依据是：title，publish_time，tags
        :param title: 标题
        :param publish_time: 文章发布时间
        :param tags: 版块
        :return: 已经存在就返回1（True）
        '''
        title = pymysql.escape_string(title)
        sqlagr = "select id from fa_cms_archives where title='{}' and publishtime='{}' and tags='{}';".format(
            title, publishtime, tags)
        rows = self.cursor.execute(sqlagr)
        if rows >= 1:
            self.logger.error("archives表中数据已存在，文章链接：{}".format(article_url))
            return 1
        return 0

    def insert_archives(self,article_url,channel_id,model_id,title,flag,image,attachfile,keywords,description,tags,weigh,views,comments,likes,dislikes,diyname,createtime,publishtime,status,power,*args,**kwargs):
        ''' 插入数据库 '''
        if len(title)>=200:
            title = title[0:200]
        title = pymysql.escape_string(title)
        image = pymysql.escape_string(image)
        attachfile = pymysql.escape_string(attachfile)
        sqlagr = '''INSERT INTO fa_cms_archives set `channel_id`="{}",`model_id`="{}",`title`="{}",`flag`="{}",`image`="{}",`attachfile`="{}",`keywords`="{}",`description`="{}",`tags`="{}",`weigh`="{}",`views`="{}",`comments`="{}",`likes`="{}",`dislikes`="{}",`diyname`="{}",`createtime`="{}",`publishtime`="{}",`status`="{}",`power`="{}";'''.format(
            channel_id, model_id, title, flag, image, attachfile, keywords, description, tags, weigh, views, comments, likes,dislikes, diyname, createtime, publishtime, status, power)
        rows = self.cursor.execute(sqlagr)
        self.con.commit()
        if rows<1:
            self.logger.error("插入archives表错误：插入失败，文章链接：{}".format(article_url))
            return False
        return True

    def filder_addonnews(self,id):
        ''' 用来判断数据库中fa_cms_addonnews表是否会出现错误 '''
        ''' 返回为 1，则数据已存在 '''
        sqlagr = "select id from fa_cms_addonnews where id={};".format(id)
        rows = self.cursor.execute(sqlagr)
        if rows >= 1:
            self.logger.error("addonnews表内容已存在错误：内容表中数据已存在，id={}".format(id))
            return 1
        return 0

    def insert_addonnews(self,id,content,author,style,*args,**kwargs):
        ''' 插入fa_cms_addonnews表 '''
        content = pymysql.escape_string(content)
        author = pymysql.escape_string(author)

        sqlagr = 'insert into fa_cms_addonnews(id,content,author,style) values ("{}","{}","{}","{}");'.format(id,content,author,style)
        row = self.cursor.execute(sqlagr)
        self.con.commit()
        if row<1:
            self.logger.error("插入addonnews表失败，文章id={}".format(id))
            return False
        return True

    def id_archives(self,title, publishtime, tags,*args,**kwargs):
        ''' 查询这条数据的id '''
        title = pymysql.escape_string(title)
        self.cursor.execute(
            "select id from fa_cms_archives where title='{}' and publishtime='{}' and tags='{}';".format(title, publishtime, tags))
        id = self.cursor.fetchone()[0]
        return id

    def insert_mysql(self,kwargs_dict):
        passed_archives = self.filder_archives(**kwargs_dict)
        if not passed_archives:
            self.insert_archives(**kwargs_dict)

        id = self.id_archives(**kwargs_dict)
        passed_addonnews = self.filder_addonnews(id)
        if passed_addonnews:
            return True
        return self.insert_addonnews(id=id,**kwargs_dict)



if __name__ == '__main__':
    # 以下是测试时使用,有必要的话重新编写测试
    yiban = YibanModel()
    # yiban.insert("news", "test_block", "test_title", "1234567890", "dong", "", "content123", "1234567890")