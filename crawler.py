from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from homeland.spiders.xfjy_spider import XfjySpider
from homeland.spiders.info_spider import InfoSpider
from homeland.spiders.official_spider import OfficialSpider
from homeland.spiders.yiban_spider import YibanSpider
from configparser import ConfigParser

config = ConfigParser()
def read_user(user_section):
    config.read("/home/py/project/homeland/homeland/info.conf")
    if config.has_section(user_section):
        username = config.get(user_section,"username")
        password = config.get(user_section,"password")
        source_type = config.get(user_section,"source_type")
        return username,password,source_type
    else:
        raise Exception("读取信息门户账号密码出现错误")

def read_user_yiban(user_section):
    config.read("/home/py/project/homeland/homeland/info.conf")
    if config.has_section(user_section):
        username = config.get(user_section,"username")
        password = config.get(user_section,"password")
        return username,password
    else:
        raise Exception("读取信息门户账号密码出现错误")

if __name__ == '__main__':
    settings = get_project_settings()
    # print(os.path.realpath(__file__))
    process = CrawlerProcess(settings)

    process.crawl(XfjySpider)
    student_username,student_password,student_type = read_user("student_user")
    teacher_username,teacher_password,teacher_type = read_user("teacher_user")
    process.crawl(InfoSpider,username = student_username,password=student_password,source_type=student_type)
    process.crawl(InfoSpider,username = teacher_username,password=teacher_password,source_type=teacher_type)
    process.crawl(OfficialSpider)

    yiban_username,yiban_password = read_user_yiban("yiban_dong")
    process.crawl(YibanSpider,username = yiban_username,pssword = yiban_password)
    process.start()

