from scrapy import cmdline

cmdline.execute("scrapy crawl zhihuCrawler -s JOBDIR=crawls/somespider-1".split())