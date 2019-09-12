# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import scrapy
import pymysql
import codecs
import pymysql.cursors
from twisted.enterprise import adbapi
from JingdongSpider.items import JingdongspiderItem

from JingdongSpider.settings import IMAGES_STORE as images_store
from scrapy.pipelines.images import ImagesPipeline
from scrapy.utils.project import get_project_settings
import os
import re
import hashlib


class JingdongspiderPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparams = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWD'],
            charset='utf8',
            cursorclass=pymysql.cursors.DictCursor,
            use_unicode=False,
        )
        dbpool = adbapi.ConnectionPool('pymysql', **dbparams)
        return cls(dbpool)
    def process_item(self, item, spider):
        query = self.dbpool.runInteraction(self._conditional_insert, item)
        return item

    def _conditional_insert(self, tx, item):
        sql = """insert into item_data(typename, itemname, food_name, store_name, item_urls) 
        values(%s, %s, %s, %s, %s)"""
        params = (item['typename'], item['itemname'], item['food_name'], item['store_name'], item['item_urls'])
        tx.execute(sql, params)


class JingdongspiderImagePipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        for i_url in item['item_url']:
            item['i_url'] = i_url
            typename = item['typename']
            item = JingdongspiderItem(i_url=i_url, typename=typename)
            yield scrapy.Request(url=i_url, meta={'item': item})

    def file_path(self, request, response=None, info=None):
        item = request.meta['item']
        typename = (item['typename']).replace('特产', 'specialty').replace('食品', 'food').replace('酒水', 'drinks').replace('生鲜', 'fresh')
        sha1 = hashlib.sha1()
        sha1.update(item['i_url'].encode('utf8'))
        apath = "./" + typename + '/'
        path = apath + sha1.hexdigest() + '.jpg'
        return path

    def item_completed(self, results, item, info):
        print(results)
        return item

