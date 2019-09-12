# -*- coding: utf-8 -*-
import scrapy
import random
import re
import json
from scrapy import Selector
from JingdongSpider.items import JingdongspiderItem
import JingdongSpider.settings
from JingdongSpider.settings import MY_USER_AGENT1

class FoodSpiderSpider(scrapy.Spider):
    name = 'food_spider'
    # allowed_domains = ['https://www.jd.com/']
    start_urls = ['https://www.jd.com/']

    header = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        # 'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        # 'Connection': 'keep-alive',
        'Referer': 'https://www.jd.com/',
        # 'User-Agent': 'Opera/9.80 (Windows NT 6.1; U; zh-cn) Presto/2.9.168 Version/11.50',
    }
    def start_requests(self):
        user_agent = JingdongSpider.settings.MY_USER_AGENT1
        agent = random.choice(user_agent)
        self.header['User_Agent'] = agent
        foodtype = ['f01e73a0', '92d97d64', '70539aa6']
        # 酒水， 食品， 特产分类的编号
        for i in foodtype:
            start_urls = 'https://storage.360buyimg.com/portalstatic/static/pc.config.' + i + '.js'
        # 三个分类的网址
        if i == '70539aa6':
            yield scrapy.Request(url=start_urls, callback=self.parse1, headers=self.header)
        #     跳转到特产大分类
        if i == '92d97d64':
            print(start_urls)
        #     yield scrapy.Request(url=start_urls, callback=self.parse2, headers=self.header)
        #     跳转到食品大分类
        if i == 'f01e73a0':
            yield scrapy.Request(url=start_urls, callback=self.parse3, headers=self.header)
            print(start_urls)
        #     跳转到酒水大分类



    def parse1(self, response):
       #  特产大分类
       html = Selector(response)
       a = ','.join(html.xpath('/html/body/p/text()').extract())
       b = str(re.findall("\[.*\]", a)).replace("['[", "").replace("]']", "")
       # print(b)
       jl = json.loads(b)
       childrens = jl['childrens']
       childrens = str(childrens)
       dataSource = re.findall('"dataSource":(.*?),"datapool"', a)
       dataSource = dataSource[0]
       js = json.loads((dataSource))
       for c in js:
           children = c["children"]
           children1 = children[1:]
           # print(children1)
           for i in children1:
               children2 = i['children']
               # print(children2)
               for m in children2:
                   children3 = m['children']
                   # print(children3)
                   for n in children3:
                       itemname = n['title']
                       itemurl = n['url']
                       print(itemname, itemurl)
#                        小分类的名字及网址
                       yield scrapy.Request(url=itemurl, callback=self.parse_url, headers=self.header)

    def parse2(self, response):
        # 食品大分类
        html = Selector(response)
        a = ','.join(html.xpath('/html/body/p/text()').extract())
        # print(a)
        b = str(re.findall("data: .*\}", a)).replace("['data: [", "").replace("]}']", "")
        # print(b)
        childrens = str(re.findall('"bgColor":"rgba\(246,246,246,1\)"\},\"childrens":(.*)\]', b)).replace("['", "").replace("']", "")
        dataSource = str(re.findall('"dataSource":(.*?),"tabDashType"', childrens)).replace("['", "").replace("']", "")
        print(dataSource)
        jl = json.loads((dataSource))
        for c in jl:
            # print(c)
            children = c['children']
            for m in children:
                children2 = m['children']
                # print(children2)
                # print(len(children2))
                # print('\n')
                for n in children2:
                    if len(children2) < 7:
                        itemname = n['name']
                        itemurl = n['link']
                        print(itemname, itemurl)
                    else:
                        children3 = n['children']
                        # print(children3)
                        for p in children3:
                            # print(p)
                            itemname = p['name']
                            itemurl = p['link']
                            # print(itemname, itemurl)
                            yield scrapy.Request(url=itemurl, callback=self.parse_url, headers=self.header)

    def parse3(self, response):
        # 酒水大分类
        html = Selector(response)
        a = ','.join(html.xpath('/html/body/p/text()').extract())
        # print(a)
        b = str(re.findall("data: .*\}", a)).replace("['data: [", "").replace("]}']", "")
        # print(b)
        childrens = str(re.findall('"dataSource":(.*?),"tabDashType"', b)).replace("['", "").replace("']", "")
        # print(childrens)
        # print(type(childrens))
        # print(len(childrens))
        jl = json.loads(childrens)
        for m in jl:
            children1 = m['children']
            # print(children1)
            for n in children1:
                children2 = n['children']
                # print(children2)
                # print(len(children2))
                for p in children2:
                    if len(children2) > 2:
                        pass
                        # itemname = p['name']
                        # itemurl = p['link']
                        # print(itemname, itemurl)
                    else:
                        children3 = p['children']
                        # print(children3)
                        for q in children3:
                            # print(p)
                            itemname = q['name']
                            itemurl = q['link']
                            # print(itemname, itemurl)
                            yield scrapy.Request(url=itemurl, callback=self.parse_url, headers=self.header)

    def parse_url(self, response):
        # 实现小分类里的自身循环和跳转到下一级具体商品页面
        html = Selector(response)
        id  = html.xpath('//*[@id="plist"]/ul/li/div/@data-sku').extract()
        if len(id) == 0:
            id = html.xpath('//*[@id="J_goodsList"]/ul/li/@data-sku').extract()
        for i in id:
            foodurl = 'https://item.jd.com/' + i + '.html'
            # print(foodurl)
            yield scrapy.Request(url=foodurl, callback=self.parse_food, headers=self.header)
#             跳转到具体商品的页面
    def parse_food(self, response):
        html = Selector(response)
        foodname = html.xpath("/html/body/div[6]/div/div[2]/div[1]/text()").extract()
        print(foodname)



