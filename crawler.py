from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from homeland.spiders.xfjy_spider import xfjy

if __name__ == '__main__':
    settings = get_project_settings()
    # print(os.path.realpath(__file__))
    process = CrawlerProcess(settings)
    process.crawl(xfjy)
    process.start()