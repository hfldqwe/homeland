from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from homeland.spiders.xfjy_spider import XfjySpider
from homeland.spiders.info_spider import InfoSpider


def crawl_spider(process,spider):
    process.crawl(spider)
    process.start()

if __name__ == '__main__':
    settings = get_project_settings()
    # print(os.path.realpath(__file__))
    process = CrawlerProcess(settings)
    process.crawl(XfjySpider)
    process.crawl(InfoSpider)
    process.start()

