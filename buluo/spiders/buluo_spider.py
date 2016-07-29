# -*- coding: utf8 -*-

import scrapy
import codecs
import json
import MySQLdb
import base64
import logging
import traceback

from buluo.items import PostItem
from buluo.items import CommentItem

class BuluoSpider(scrapy.Spider):

    name = "buluo_spider"
    download_delay = 0.1
    logger = logging.getLogger('buluo_spider')

    def __init__(self, category=None, bid = None, *args, **kwargs):
        super(BuluoSpider, self).__init__(*args, **kwargs)
        self.bid = bid
        self.start_urls = ['http://buluo.qq.com/cgi-bin/bar/post/get_post_by_page?bid=%s&num=20&start=0&source=2&r=0.26335205588845634&bkn=' % bid]


    def parse(self, response):

        data = json.loads(response.body)
        try:
            post_num = data['result']['total']
            print '=============================='
            print post_num
            for start in xrange(0,post_num,20):
                url = "http://buluo.qq.com/cgi-bin/bar/post/get_post_by_page?bid=%s&num=20&start=%d&source=2&r=0.26335205588845634&bkn=" % (
                    self.bid,start)
                yield scrapy.Request(url, callback=self.parse_post_json)
        except Exception as e:
            self.logger.info(traceback.format_exc())
            self.logger.info(response.body.decode('utf8'))

    def parse_post_json(self, response):

        data = json.loads(response.body)
        try:
            for post in data['result']['posts']:
                item = PostItem()
                item['bid'] = str(post['bid'])
                item['pid'] = post['pid']
                item['title'] = post['title']
                item['content'] = post['post']['content']
                yield item

            #爬取话题的评论    
            for start in xrange(0, post['total_comment']):
                url = "http://buluo.qq.com/cgi-bin/bar/post/get_comment_by_page_v2?bid=%s&pid=%s&num=20&start=%d&barlevel=1&r=0.6100480090786624" % (
                    self.bid, post['pid'], start)
                yield scrapy.Request(url, callback=self.parse_comment_json)
        
        except Exception as e:
            self.logger.info(traceback.format_exc())
            self.logger.info(response.body.decode('utf8'))

    def parse_comment_json(self, response):

        data = json.loads(response.body)
        try:
            for comment in data['result']['comments']:
                item = CommentItem()
                item['bid'] = str(comment['bid'])
                item['pid'] = comment['pid']
                item['comment_index'] = int(comment['index'])
                item['content'] = comment['comment']['content']
                yield item
        except Exception as e:
            self.logger.info(traceback.format_exc())
            self.logger.info(response.body.decode('utf8'))



        