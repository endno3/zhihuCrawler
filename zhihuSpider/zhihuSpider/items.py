# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class topicItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    id = scrapy.Field()
    name = scrapy.Field()
    desc = scrapy.Field()


class answerItem(scrapy.Item):
    # 抓取回答id
    # 问题id
    # 用户名
    # 回答正文
    id = scrapy.Field()
    question_id = scrapy.Field()
    user = scrapy.Field()
    answer = scrapy.Field()


class questionItem(scrapy.Item):
    # 话题id
    # 问题id
    # 问题
    topic_id = scrapy.Field()
    question_id = scrapy.Field()
    question = scrapy.Field()

