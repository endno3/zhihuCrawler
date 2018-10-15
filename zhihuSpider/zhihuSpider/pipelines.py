# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
from zhihuSpider.items import topicItem
from zhihuSpider.items import answerItem
from zhihuSpider.items import questionItem
from scrapy.exceptions import  DropItem

# 处理不同item 并且存到数据库内
class ZhihuspiderPipeline(object):
    # def __init__(self, uri, db):
    #     self.DB_URL = uri
    #     self.DB_NAME = db

    @classmethod
    def from_crawler(cls, crawler):
        cls.DB_URL = crawler.settings.get('MONGODB_DB_URI', "mongodb://localhost:27017")
        cls.DB_NAME = crawler.settings.get('MONGODB_DB_NAME', 'Zhihu')
        return cls()

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.DB_URL)
        self.db = self.client[self.DB_NAME]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        if isinstance(item, topicItem):
            self.db.Topic.insert(dict(item))
        elif isinstance(item, answerItem):
            self.db.Answer.insert(dict(item))
        elif isinstance(item, questionItem):
            self.db.Question.insert(dict(item))
        else:
            raise DropItem
