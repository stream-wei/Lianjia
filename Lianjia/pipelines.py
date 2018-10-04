# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


import csv
import pymysql
import operator


class LianjiaPipeline(object):

    def process_item(self, item, spider):
        # f = open('/Users/stream/PycharmProjects/Lianjia/lianjia.csv', 'a+')
        # write = csv.writer(f)
        # write.writerow((item['title'], item['community'], item['model'], item['area'], \
        #                 item['focus_num'], item['watch_num'], item['time'], item['price'], item['average_price'],
        #                 item['link'], \
        #                 item['city'], item['page']))
        db = pymysql.connect("localhost", "stream", "weiXI!@#456", "stream")
        cursor = db.cursor()
        area = item['area'].lstrip().rstrip().replace("平米", "")
        focus_num = item['focus_num'].lstrip().rstrip().replace("人关注", "")
        watch_num = item['watch_num'].lstrip().rstrip().replace("共", "").replace("次带看", "")
        time = item['time'].lstrip().rstrip()
        if time.endswith("个月以前发布"):
            time = int(time[0:len(time) - len("个月以前发布")]) * 30
        elif time.endswith("天以前发布"):
            time = int(time[0:len(time) - len("天以前发布")])
        elif time.endswith("年前发布"):
            time = time[0:1]
            if operator.eq(time, "一"):
                time = 12 * 30
            elif operator.eq(time, "二"):
                time = 24 * 30
            else:
                time = 25 * 30
        else:
            time = 26 * 30

        average_price = item['average_price'].replace("单价", "").replace("元/平米", "")
        sql = "insert into ershoufang(district, zone, community, detail, model, area, focus_num, watch_num, ctime,ctime_full," \
              " price, average_price,link) " \
              "value ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" % \
              (item['district'], item['zone'], item['community'], item['title'], item['model'], area, focus_num,
               watch_num, time, item['time'], item['price'], average_price, item['link'])
        cursor.execute(sql)
        db.commit()
        db.close()
        return item


class LianjiaQuPipeline(object):

    def process_item(self, item, spider):
        f = open('D:\\ideaProjects\\python\\Lianjia\\lianjiaqu.csv', 'a+')
        write = csv.writer(f)
        write.writerow((item['rootName'], item['name']))
        return item
