import redis
from configparser import ConfigParser

def redis_conf(section):
    config = ConfigParser()
    config.read("/home/py/project/homeland/homeland/info.conf")
    if config.has_section(section):
        host = config.get(section,"host")
        port = config.get(section,"port")
        password = config.get(section,"password")
        db = config.get(section,"db")
        return host,port,password,db
    else:
        raise Exception("读取redis配置出现错误")


class FilterUrl():
    def __init__(self):
        host,port,password,db = redis_conf("redis_local")
        self.re = redis.Redis(host=host,port=port,password=password,db=db)
        self.name = "xfjy_article_url"

    def filter(self,url):
        '''
        用来过滤url，如果没有，exist为None
        '''
        exist = self.re.sismember(self.name,url)
        return exist

    def add(self,url):
        self.re.sadd(self.name,url)

    def test(self):
        print(self.filter("1"))


if __name__ == '__main__':
    filter_url = FilterUrl()
    filter_url.test()
    # print(redis_conf("redis_local"))
