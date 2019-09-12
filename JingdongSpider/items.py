# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JingdongspiderItem(scrapy.Item):
    # define the fields for your item here like:
    typename = scrapy.Field()
    # 大分类名字
    itemname = scrapy.Field()
    # 小分类名字
    foodurl = scrapy.Field()
    item_urls = scrapy.Field()
    # 以字符串形式保存在数据库中
    item_url = scrapy.Field()
    #以数组形式存在，图片保存时的下载链接
    food_name = scrapy.Field()
    # 商品名
    store_name = scrapy.Field()
    # 店铺名
    i_url = scrapy.Field()
    itemurl = scrapy.Field()
