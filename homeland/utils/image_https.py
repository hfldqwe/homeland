# 用来将缩略图链接转化为HTTPS链接

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

class ConvertImage():
    def __init__(self,*args,**kwargs):
        host, port, username, password, db = mysql_conf("mysql_235")
        self.con = pymysql.connect(
            host = host,
            port = port,
            user = username,
            password = password,
            db = db,
        )
        self.cursor = self.con.cursor()

    def convert_https(self):
        for id,url in self._get_image_urls():
            if url:

                if "https"  in url:
                    continue

                url = url.replace("http","https")
                sqlarg = "update fa_cms_archives set image='{}' where id={};".format(url,id)
                self.cursor.execute(sqlarg)

        self.con.commit()

    def _get_image_urls(self):
        sqlarg = "select id,image from fa_cms_archives;"
        self.cursor.execute(sqlarg)

        return self.cursor.fetchall()

if __name__ == '__main__':
    convert = ConvertImage()
    convert.convert_https()