# -*- coding: utf-8 -*-

import math
import random
import time

import requests
import scrapy
from lxml import etree

from ..items import LianjiaItem


class LianjiaSpider(scrapy.Spider):
    name = 'lianjiaspider'
    allowed_domains = ['sh.lianjia.com']
    start_urls = 'http://sh.lianjia.com/ershoufang/'

    def start_requests(self):
        user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:60.0) Gecko/20100101 Firefox/60.0'
        headers = {'User-Agent': user_agent}
        # 包含yield语句的函数是一个生成器，每次产生一个值，函数被冻结，被唤醒后再次产生一个值
        yield scrapy.Request(url=self.start_urls, headers=headers, method='GET', callback=self.parse)
        # callback指定该请求返回的Response由哪个函数来处理

    def parse(self, response):
        user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:60.0) Gecko/20100101 Firefox/60.0'
        headers = {'User-Agent': user_agent}  # 用headers伪装浏览器
        lists = response.body.decode('utf-8')
        selector = etree.HTML(lists)
        # 在进行网页抓取的时候，分析定位html节点
        # 将文件读入，解析成树，然后根据路径定位到每个节点
        area_list = selector.xpath('/html/body/div[3]/div/div[1]/dl[2]/dd/div[1]/div/a')
        # etree.HTML得到的内容可以直接使用xpath
        for area in area_list:
            try:
                # ['浦东', '闵行', '宝山', '徐汇'...]
                area_hanzi = area.xpath('text()').pop()
                # ['/ershoufang/pudong/', '/ershoufang/minhang/', '/ershoufang/baoshan/'...]
                area_pinyin = area.xpath('@href').pop().split('/')[2]
                area_url = 'http://sh.lianjia.com/ershoufang/{}/'.format(area_pinyin)
                yield scrapy.Request(url=area_url, headers=headers, callback=self.qu_detail,
                                     meta={"id1": area_hanzi, "id2": area_pinyin})
            except Exception:
                pass

    def qu_detail(self, response):
        user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:60.0) Gecko/20100101 Firefox/60.0'
        headers = {'User-Agent': user_agent}  # 用headers伪装浏览器
        lists = response.body.decode('utf-8')
        selector = etree.HTML(lists)
        qu_list = selector.xpath('/html/body/div[3]/div/div[1]/dl[2]/dd/div[1]/div[2]/a')
        for qu in qu_list:
            try:
                qu_hanzi = qu.xpath('text()').pop()
                qu_pinyin = qu.xpath('@href').pop().split('/')[2]
                area_url = 'http://sh.lianjia.com/ershoufang/{}/'.format(qu_pinyin)
                yield scrapy.Request(url=area_url, headers=headers, callback=self.detail_url,
                                     meta={"id1": qu_hanzi, "id2": qu_pinyin, "id3": response.meta["id1"]})
            except Exception:
                pass
            # yield item
        pass

    def detail_url(self, response):
        user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:60.0) Gecko/20100101 Firefox/60.0'
        lists = response.body.decode('utf-8')
        selector = etree.HTML(lists)
        count_list = selector.xpath('/html/body/div[4]/div[1]/div[2]/h2/span/text()')
        count = math.ceil(int(count_list[0]) / 30)
        for i in range(1, count):
            url = 'http://sh.lianjia.com/ershoufang/{}/pg{}/'.format(response.meta["id2"], str(i))
            time.sleep(random.randint(1, 5))  # 随机等待1-5秒
            try:
                contents = requests.get(url)
                contents = etree.HTML(contents.content.decode('utf-8'))
                houselist = contents.xpath('/html/body/div[4]/div[1]/ul/li')
                for house in houselist:
                    try:
                        item = LianjiaItem()
                        item['page'] = i
                        item['district'] = response.meta["id3"]  # 区
                        item['zone'] = response.meta["id3"]  # 板块
                        item['community'] = house.xpath('div[1]/div[2]/div/a/text()').pop()  # 小区
                        item['title'] = house.xpath('div[1]/div[1]/a/text()').pop()
                        item['model'] = house.xpath('div[1]/div[2]/div/text()').pop().split('|')[1]  # 户型
                        item['area'] = house.xpath('div[1]/div[2]/div/text()').pop().split('|')[2]  # 面积
                        item['focus_num'] = house.xpath('div[1]/div[4]/text()').pop().split('/')[0]
                        item['watch_num'] = house.xpath('div[1]/div[4]/text()').pop().split('/')[1]
                        item['time'] = house.xpath('div[1]/div[4]/text()').pop().split('/')[2]
                        item['price'] = house.xpath('div[1]/div[6]/div[1]/span/text()').pop()  # 总价
                        item['average_price'] = house.xpath('div[1]/div[6]/div[2]/span/text()').pop()  # 均价
                        item['link'] = house.xpath('div[1]/div[1]/a/@href').pop()
                        self.url_detail = house.xpath('div[1]/div[1]/a/@href').pop()
                    except Exception:
                        pass
                    yield item
            except Exception:
                pass
        pass
