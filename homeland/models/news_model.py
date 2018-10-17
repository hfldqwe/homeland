import pymysql
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
    '''
    用来说明参数的意义：
    source_type —— 这个是news，最基本的一个类型说明
    block_type —— 这个是版块的类型，如：先锋家园，地测等等，而且一个文章可以有多个标签
    title —— 标题
    create_time —— 爬取文章的发布时间
    author —— 作者
    attachment —— 附件以及地址
    content —— 文章内容
    spider_time —— 爬取的时间
    '''
    def __init__(self):
        host, port, username, password, db = mysql_conf("mysql_235")
        self.con = pymysql.connect(
            host = host,
            port = port,
            user = username,
            password = password,
            db = db,
        )
        self.cursor = self.con.cursor()

    def filder_news(self,title,create_time,block_type):
        '''
        用来过滤掉重复的参数，判断依据是：title，create_time，block_type
        :param title: 标题
        :param create_time: 文章发布时间
        :param block_type: 版块
        :return: 已经存在就返回1（True）
        '''
        title = pymysql.escape_string(title)
        sqlagr = "select id from fa_school_news where title='{}' and create_time='{}' and block_type='{}';".format(
            title, create_time, block_type)
        rows = self.cursor.execute(sqlagr)
        if rows != 0:
            return 1

    def insert_news(self,source_type, block_type, title, create_time, author, attachment, content, spider_time):
        ''' 插入数据库 '''
        if len(title)>=200:
            title = title[0:200]
        title = pymysql.escape_string(title)
        content = pymysql.escape_string(content)
        sqlagr = '''INSERT INTO fa_school_news(source_type,block_type,title,create_time,author,attachment,content,spider_time,remark,views,likes,status) VALUE('{}','{}','{}','{}','{}','{}',"{}",'{}','{}',{},{},{});'''.format(
            source_type, block_type, title, create_time, author, attachment, content, spider_time, "", "0", "0", "1")
        rows = self.cursor.execute(sqlagr)
        self.con.commit()
        if rows<1:
            return "插入数据库错误"

    def id_news(self,title, create_time,block_type):
        ''' 查询这条数据的id '''
        title = pymysql.escape_string(title)
        self.cursor.execute(
            "SELECT id FROM fa_school_news where title='{}' and create_time='{}' and block_type='{}';".format(title, create_time,block_type))
        id = self.cursor.fetchone()[0]
        return id

    def tags(self,block_type,id):
        '''
        判断tags是否存在，存在就直接修改，不存在就创建一个
        :param block_type:
        :return:
        '''
        row = self.cursor.execute("select id,archives,nums from fa_cms_tags where `name`='{}';".format(block_type))
        if row != 0:
            type_id, archives, nums = self.cursor.fetchone()
            if type_id:
                archives_set = set(archives.split(","))
                # 判断这个id是否在archives中，若存在，则不添加，若不存在，则添加
                if str(id) not in archives_set:
                    archives = archives + "," + str(id)
                    nums = int(nums) + 1
                    row = self.cursor.execute("update fa_cms_tags set archives='{}',nums={} where id={};".format(archives, nums, type_id))
                    self.con.commit()
        else:
            self.cursor.execute(
                "insert into fa_cms_tags (`name`,archives,nums) value ('{}','{}',{});".format(block_type, id, 1))
            self.con.commit()

if __name__ == '__main__':
    # 以下是测试时使用,有必要的话重新编写测试
    yiban = YibanModel()
    # yiban.insert("news", "test_block", "test_title", "1234567890", "dong", "", "content123", "1234567890")