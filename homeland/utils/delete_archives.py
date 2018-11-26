# 用于删除archives表中数据
# 时间戳转化出现错误，删掉旧的数据，重新抓一边
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

class DeleteOfficial():
    def __init__(self, *args, **kwargs):
        host, port, username, password, db = mysql_conf("mysql_235")
        self.con = pymysql.connect(
            host=host,
            port=port,
            user=username,
            password=password,
            db=db,
        )
        self.cursor = self.con.cursor()

    def delete(self):
        content_ids = self._get_content_id()

        for content_id in content_ids:
            content_id = content_id[0]
            sqlarg = "delete from fa_cms_addonnews where id={};".format(content_id)

            self.cursor.execute(sqlarg)

        self.con.commit()

    def _get_content_id(self):
        sqlarg = "select id from fa_cms_archives where channel_id=4;"
        self.cursor.execute(sqlarg)

        content_ids = self.cursor.fetchall()
        return content_ids

if __name__ == '__main__':
    delete = DeleteOfficial()
    delete.delete()
