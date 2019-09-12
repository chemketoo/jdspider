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
        for i in range(2):
            if i == 0:
                start_urls = 'https://fresh.jd.com/'
                yield scrapy.Request(url=start_urls, callback=self.parse4, headers=self.header)
                # 跳转到生鲜大分类，生鲜大分类，生鲜大分类为网页， 下面三个分类为json文件
            if i == 1:
                foodtype = ['f01e73a0', '92d97d64', '70539aa6']
                # 酒水， 食品， 特产分类的编号
                for i in foodtype:
                    start_urls = 'https://storage.360buyimg.com/portalstatic/static/pc.config.' + i + '.js'
                # 三个分类的网址
                if i == '70539aa6':
                    yield scrapy.Request(url=start_urls, callback=self.parse1, headers=self.header)
                #     跳转到特产大分类
                if i == '92d97d64':
                    yield scrapy.Request(url=start_urls, callback=self.parse2, headers=self.header)
                #     跳转到食品大分类
                if i == 'f01e73a0':
                    yield scrapy.Request(url=start_urls, callback=self.parse3, headers=self.header)
                    print(start_urls)
            #     跳转到酒水大分类



    def parse1(self, response):
       #  特产大分类
       typename = '特产'
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
       # print(js)
       for c in js:
           children = c["children"]
           children1 = children[1:]
           for i in children1:
               children2 = i['children']
               # print(children2)
               for m in children2:
                   children3 = m['children']
                   # print(children3)
                   for n in children3:
                       itemname = n['title']
                       itemurl = n['url']
                       # print(itemname, itemurl)
#                        小分类的名字及网址
                       item = JingdongspiderItem(itemname=itemname, typename=typename, itemurl=itemurl)
                       yield scrapy.Request(url=itemurl, callback=self.parse_url, headers=self.header, meta={'item': item})

    def parse2(self, response):
        # 食品大分类
        typename = '食品'
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
                        item = JingdongspiderItem(itemname=itemname, typename=typename, itemurl=itemurl)
                        yield scrapy.Request(url=itemurl, callback=self.parse_url, headers=self.header)
                    else:
                        children3 = n['children']
                        # print(children3)
                        for p in children3:
                            # print(p)
                            itemname = p['name']
                            itemurl = p['link']
                            # print(itemname, itemurl)
                            #                        小分类的名字及网址
                            item = JingdongspiderItem(itemname=itemname, typename=typename, itemurl=itemurl)
                            yield scrapy.Request(url=itemurl, callback=self.parse_url, headers=self.header, meta={'item': item})

    def parse3(self, response):
        # 酒水大分类
        typename = '酒水'
        html = Selector(response)
        a = ','.join(html.xpath('/html/body/p/text()').extract())
        # print(a)
        b = str(re.findall("data: .*\}", a)).replace("['data: [", "").replace("]}']", "")
        # print(b)
        childrens = str(re.findall('"dataSource":(.*?),"tabDashType"', b)).replace("['", "").replace("']", "")
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
                    # 推荐区的和后面的重叠，所以pass
                    else:
                        children3 = p['children']
                        # print(children3)
                        for q in children3:
                            # print(p)
                            itemname = q['name']
                            itemurl = q['link']
                            # print(itemname, itemurl)
                            #                        小分类的名字及网址
                            item = JingdongspiderItem(itemname=itemname, typename=typename, itemurl=itemurl)
                            yield scrapy.Request(url=itemurl, callback=self.parse_url, headers=self.header, meta={'item': item})

    def parse4(self, response):
        # 生鲜大分类，抓取小分类的方法和其他三种有区别
        typename = '生鲜'
        html = Selector(response)

        script = str(html.xpath('//*[@id="J_container"]/script[1]').extract())
        # print(script)
        jl = re.findall('children:\[\{ NAME.*?o2:1\}\]', script)
        for i in jl:
            m = re.findall('\{ NAME.*?\}', i)
            for n in m:
                # print(n)
                itemname = str(re.findall("NAME:(.*?),URL", n)).replace("\\\\'", "").replace("\\\\',", "").replace('["', '').replace('"]', '')
                itemurl = str(re.findall("URL(.*?)\\',id:", n)).replace('\\\\"]', '').replace('[":', '').replace(' ', '').replace("\\\\'", '')
                if 'http' not in itemurl:
                    itemurl = itemurl.replace('//', 'https://')
                #     部分网址以//开头，需要修改
                # print(itemname, itemurl)
                # print(itemurl)
                item = JingdongspiderItem(itemname=itemname, typename=typename, itemurl=itemurl)
                yield scrapy.Request(url=itemurl, callback=self.parse_url, headers=self.header, meta={'item': item})



    def parse_url(self, response):
        # 实现小分类里的自身循环和跳转到下一级具体商品页面
        item = response.meta['item']
        html = Selector(response)
        id = html.xpath('//*[@id="plist"]/ul/li/div/@data-sku').extract()
        if len(id) == 0:
            id = html.xpath('//*[@id="J_goodsList"]/ul/li/@data-sku').extract()
        if len(id) > 0:
            # 小分类有产品才能进行自身循环和下一级具体页面
            for i in id:
                foodurl = 'https://item.jd.com/' + i + '.html'
                # print(foodurl)
                itemname = item['itemname']
                typename = item['typename']
                itemurl = item['itemurl']
                item = JingdongspiderItem(itemname=itemname, typename=typename, foodurl=foodurl, itemurl=itemurl)
                # 不加这三行会出现数据库数据重复
                # print(i)
                yield scrapy.Request(url=foodurl, callback=self.parse_food, headers=self.header, meta={'item': item})
            #             跳转到具体商品的页面

            itemurl = str(item['itemurl'])
            # print(itemurl)
            page = str(html.xpath('//*[@id="J_topPage"]/span/i/text()').extract()).replace("['", "").replace("']", "")
            # 获取小分类页数
            # print(page)
            page = int(page)
            a = str(re.findall('http.*?#J', itemurl)).replace('#J', '').replace("['", "").replace("']", "")
            if len(a) < 3:
                a = itemurl
                for i in range(1, page + 1):
                    n = str(i)
                    next_url = a + '&page=' + n
                    print(next_url)
                    yield scrapy.Request(url=next_url, callback=self.parse_url, headers=self.header, meta={'item': item})
            else:
                for i in range(1, page + 1):
                    n = 2 * i - 1
                    n = str(n)
                    next_url = a + '&page=' + n
                    print(next_url)
                    yield scrapy.Request(url=next_url, callback=self.parse_url, headers=self.header, meta={'item': item})
    # 小分类有两种链接格式，分别用两种翻页

    def parse_food(self, response):
        # 商品界面
        item = response.meta['item']
        html = Selector(response)
        food_name = str(html.xpath("/html/body/div[6]/div/div[2]/div[1]/text()").extract()).replace("['", "").replace("']", '').replace(" ", "")
        # print(food_name)
        item['food_name'] = str(food_name).replace('\\n', '').replace("'", '').replace(',', '').replace('"', '')
        # 获取商品名
        # price = html.xpath("/html/body/div[6]/div/div[2]/div[3]/div/div[1]/div[2]/span[1]/span[2]").extract()
        # print(price)
        store_name = str(html.xpath('//*[@id="crumb-wrap"]/div/div[2]/div[2]/div[1]/div/a/text()').extract()).replace("['", "").replace("']", '')
        # print(store_name)
        item['store_name'] = store_name
        # 店铺名
        picture_url = html.xpath('//*[@id="spec-list"]/ul/li/img/@src').extract()
        # print(picture_url)
        item_url = []
        for i in picture_url:
            i = str('https:' + i.replace("n5", "n1"))
            item_url.append(i)
            # print(i)
        # print(item_url)
        #     上面大图所在的网址
        item['item_url'] = item_url
        script = str(html.xpath("/html/head/script[@charset = 'gbk']").extract())
        # print(script)
        # 包含商品下面大图所在网址的标签
        next_url = 'https:' + str(re.findall("desc:(.*?),", script)).replace('\\', '').replace("'", "").replace('[" ', '').replace('"]', '')
        # print(next_url)
#         跳转到商品大图的网址
        yield scrapy.Request(url=next_url, callback=self.parse_bigpicture, headers=self.header, meta={'item': item})

    def parse_bigpicture(self, response):
        # 下面大图
        item = response.meta['item']
        html = Selector(response)
        body = str(html.xpath('/html/body').extract())
        big_urls = re.findall('//img.*?jpg', body)
        item_url = item['item_url']
        for i in big_urls:
            big_url = 'https:' + i
            item_url.append(big_url)
            # print(big_url)
        item_urls = str(item_url)
        item['item_url'] = item_url
        # print(item_url)
        item['item_urls'] = item_urls

        yield item



