# -*- coding: utf-8 -*-
import scrapy
import json
from zhihuSpider.items import questionItem
from zhihuSpider.items import topicItem
from zhihuSpider.items import answerItem


class ZhihucrawlerSpider(scrapy.Spider):
    name = 'zhihuCrawler'
    allowed_domains = ['zhihu.com']
    start_urls = ['https://www.zhihu.com/topic/19564127/hot']

    def start_requests(self):
        return [scrapy.Request(url=self.start_urls[0], callback=self.topic_page_parse)]

    def topic_page_parse(self, response):
        # collect topic item
        topic_name_xpath = '//div[@class="TopicMetaCard-title" or @class="TopicCard-title"]//text()'
        topic_desc_xpath = '//div[@class="TopicMetaCard-description" or @class="TopicCard-description"]//text()'
        item = topicItem()
        item['id'] = response.url.split('/')[-2]
        item['name'] = response.selector.xpath(topic_name_xpath).extract()[0]
        item['desc'] = response.selector.xpath(topic_desc_xpath).extract()[0]
        yield item

        # collect topic item link(XHR)
        urls = self.topicXHR_constructor(item['id'])
        yield scrapy.Request(urls[0], callback=self.topic_link_parse)
        yield scrapy.Request(urls[1], callback=self.topic_link_parse)

        # collect question item link
        url = 'https://www.zhihu.com/api/v4/topics/%s/feeds/top_activity'%str(item['id'])
        formdata = {
            "offset": "5",
            "limit": "10",
            "include": ('data[?(target.type=topic_sticky_module)].target.data[?(target.type=answer)].target.content,'
                        'relationship.is_authorized,is_author,voting,is_thanked,is_nothelp;data[?(target.type=topic_'
                        'sticky_module)].target.data[?(target.type=answer)].target.is_normal,comment_count,voteup_'
                        'count,content,relevant_info,excerpt.author.badge[?(type=best_answerer)].topics;data[?'
                        '(target.type=topic_sticky_module)].target.data[?(target.type=article)].target.content,voteup_'
                        'count,comment_count,voting,author.badge[?(type=best_answerer)].topics;data[?(target.type=topic'
                        '_sticky_module)].target.data[?(target.type=people)].target.answer_count,articles_count,gender,'
                        'follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics;data'
                        '[?(target.type=answer)].target.annotation_detail,content,relationship.is_authorized,is_'
                        'author,voting,is_thanked,is_nothelp;data[?(target.type=answer)].target.author.badge[?'
                        '(type=best_answerer)].topics;data[?(target.type=article)].target.annotation_detail,'
                        'content,author.badge[?(type=best_answerer)].topics;data[?(target.type=question)].'
                        'target.annotation_detail,comment_count')
        }
        yield scrapy.FormRequest(url=url,
                                 method='GET',
                                 formdata=formdata,
                                 callback=self.question_link_parse)

    def topicXHR_constructor(self, topic_id):
        url_pre = 'https://www.zhihu.com/api/v3/topics/'
        return url_pre+topic_id+'/parent', url_pre+topic_id+'/children'

    def topic_link_parse(self, response):
        # collect topic_page link
        data = json.loads(response.body)
        if data:
            topics = data['data']
            for topic in topics:
                topic_id = topic['id']
                url = "https://www.zhihu.com/topic/"+str(topic_id)+'/hot'
                yield scrapy.Request(url=url, callback=self.topic_page_parse)

            is_end = data['paging']['is_end']
            if not is_end:
                url = data['paging']['next']
                yield scrapy.Request(url=url, callback=self.topic_link_parse)

    def question_link_parse(self, response):
        data = json.loads(response.body)

        if data:
            # collect question item link
            questions = data['data']
            for question in questions:
                target = question['target']
                type = target['type']
                if type == 'answer':
                    question_id = target['question']['id']
                    url = "https://www.zhihu.com/question/"+str(question_id)
                    yield scrapy.Request(url=url, callback=self.question_page_parse)

            # collect question page link
            is_end = data['paging']['is_end']
            if not is_end:
                url = data['paging']['next']
                yield scrapy.Request(url=url, callback=self.question_link_parse)

    def question_page_parse(self, response):
        # collect question item
        data_xpath = '//div[@data-zop-question]/@data-zop-question'
        data = response.selector.xpath(data_xpath).extract()[0]
        data = json.loads(data)
        id = data['id']

        item = questionItem()
        item['question_id'] = data['id']
        item['question'] = data['title']
        topics = data['topics']
        topic_ids = []
        for topic in topics:
            topic_ids.append(topic['id'])
        item['topic_id'] = topic_ids
        yield  item

        for id in topic_ids:
            url = "https://www.zhihu.com/topic/"+id+"/hot"
            scrapy.Request(url=url, callback=self.topic_page_parse)

        # collect answer item
        answers_xpath = '//div[@class="List-item"]'
        answers = response.selector.xpath(answers_xpath)
        for answer in answers:
            item = answerItem()

            info = answer.xpath("//div[@data-zop]/@data-zop").extract()[0]
            info = json.loads(info)
            item['id'] = info['itemId']
            item['question_id'] = id
            item['user'] = info['authorName']
            item['answer'] = answer.xpath('//div[@class="RichContent-inner"]//text()').extract()
            yield item

        # collect answer item link(XHR)
        url = "http://www.zhihu.com//api/v4/questions/%s/answers"%str(id)
        formdata = {
            "limit" : "5",
            "offset" : "15",
            "sort_by" :"default",
            "include" : ('data[*].is_normal,admin_closed_comment,reward_info,'
                         'is_collapsed,annotation_action,annotation_detail,collapse_reason,is_sticky,collapsed_by,'
                         'suggest_edit,comment_count,can_comment,content,editable_content,voteup_count,reshipment_'
                         'settings,comment_permission,created_time,updated_time,review_info,relevant_info,question,'
                         'excerpt,relationship.is_authorized,is_author,voting,is_thanked,is_nothelp;data[*].mark_'
                         'infos[*].url;data[*].author.follower_count,badge[*].topics')
        }
        yield scrapy.FormRequest(url=url,
                                 method='GET',
                                 formdata=formdata,
                                 callback=self.answer_link_parse)

    def answer_link_parse(self, response):
        # collect answer item
        data = json.loads(response.body)
        if data['data']:
            for p in data['data']:
                answer = answerItem()
                answer['id'] = p['id']
                answer['question_id'] = p['question']['id']
                answer['user'] = p['author']['name']
                answer['answer'] = p['content']
                yield  answer

        # collect answer page link
        is_end = data['paging']['is_end']
        if not is_end:
            yield scrapy.Request(url=data['paging']['next'], callback=self.answer_link_parse)






