# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import MySQLdb
from twisted.enterprise import adbapi
import MySQLdb.cursors
from scrapy import log
from buluo.items import PostItem
from buluo.items import CommentItem
import logging

class BuluoPipeline(object):
    def process_item(self, item, spider):
        return item


class MySQLStorePipeline(object):

    logger = logging.getLogger()

    def __init__(self, dbpool):
        self.dbpool = dbpool
        dbpool.runQuery("""
            CREATE TABLE IF NOT EXISTS post(
                id int NOT NULL AUTO_INCREMENT PRIMARY KEY,
                bid varchar(200),
                pid varchar(200),
                title varchar(500),
                content text,
                time datetime
                );
            """)

        dbpool.runQuery("""
            CREATE TABLE IF NOT EXISTS comment(
                id int NOT NULL AUTO_INCREMENT PRIMARY KEY,
                bid varchar(200),
                pid varchar(200),
                comment_index int,
                content text,
                time datetime
                );
            """)

    
    @classmethod
    def from_settings(cls, settings):
        dbargs = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWD'],
            charset='utf8',
            cursorclass = MySQLdb.cursors.DictCursor,
            use_unicode= True,
        )
        dbpool = adbapi.ConnectionPool('MySQLdb', **dbargs)
        return cls(dbpool)

    #pipeline默认调用
    def process_item(self, item, spider):
        d = self.dbpool.runInteraction(self._do_upinsert, item, spider)
        d.addErrback(self._handle_error, item, spider)
        return d
        
    #将每行更新或写入数据库中
    def _do_upinsert(self, conn, item, spider):
        if isinstance(item, PostItem):
            conn.execute("""
                insert into post(bid, pid, title, content) 
                values(%s, %s, %s, %s)
            """, (item['bid'], item['pid'], item['title'], item['content']))
        elif isinstance(item, CommentItem):
            conn.execute("""
                insert into comment(bid, pid, comment_index, content) 
                values(%s, %s, %s, %s)
            """, (item['bid'], item['pid'], item['comment_index'], item['content']))


    #异常处理
    def _handle_error(self, failure, item, spider):
        self.logger.info('%s',failure)
        string = """
                insert into post(bid, pid, title, content) 
                values(%s, %s, %s, %s)
            """ % (item['bid'], item['pid'], item['title'], item['content'])
        self.logger.info("%s", string)
        
        