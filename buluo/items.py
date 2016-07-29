# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BuluoItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class PostItem(scrapy.Item):
    bid = scrapy.Field()
    pid = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    link = scrapy.Field()

class CommentItem(scrapy.Item):
    bid = scrapy.Field()
    pid = scrapy.Field()
    comment_index = scrapy.Field()
    content = scrapy.Field()
    