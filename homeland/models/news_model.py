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

    def insert(self,source_type,block_type,title,create_time,author,attachment,content,spider_time):
        content = pymysql.escape_string(content)
        # 检查title和time是否已经有了，有了的话就抛弃这篇新闻
        sqlagr = "select id from fa_school_news where title='{}' and create_time='{}' and block_type='{}';".format(title,create_time,block_type)
        row = self.cursor.execute(sqlagr)
        if row != 0:
            return None

        # 当确认了这条数据的唯一性，然后保存进去
        sqlagr = '''INSERT INTO fa_school_news(source_type,block_type,title,create_time,author,attachment,content,spider_time,remark,views,likes,status) VALUE('{}','{}','{}','{}','{}','{}',"{}",'{}','{}',{},{},{});'''.format(source_type,block_type,title,create_time,author,attachment,content,spider_time,"","0","0","1")
        row = self.cursor.execute(sqlagr)
        self.con.commit()

        # 查询这条数据的id
        self.cursor.execute("SELECT id FROM fa_school_news where title='{}' and create_time='{}';".format(title,create_time))
        id = self.cursor.fetchone()[0]

        # 查询这个版块是否存在，存在就向里面进行修改，不存在就添加
        row = self.cursor.execute("select id,archives,nums from fa_cms_tags where `name`='{}';".format(block_type))
        if row != 0:
            type_id,archives,nums = self.cursor.fetchone()
            if type_id:
                archives = archives + "," + str(id)
                nums = int(nums)+1
                row = self.cursor.execute("update fa_cms_tags set archives='{}',nums={} where id={};".format(archives,nums,type_id))
                self.con.commit()
        else:
            self.cursor.execute("insert into fa_cms_tags (`name`,archives,nums) value ('{}','{}',{});".format(block_type,id,1))
            self.con.commit()

if __name__ == '__main__':
    # 以下是测试时使用
    yiban = YibanModel()
    yiban.insert("news", "test_block", "test_title", "1234567890", "dong", "", "content123", "1234567890")