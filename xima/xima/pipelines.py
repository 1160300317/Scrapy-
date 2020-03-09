# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import openpyxl

class XimaPipeline(object):
    def __init__(self):
        self.wb = openpyxl.Workbook()
        self.ws = self.wb.active
        self.ws.append(['ID名', '文件链接'])

    def process_item(self, item, spider):
        if item['href'].isspace() :
            pass
        else:
            line = [item['id'], item['href']]
            self.ws.append(line)
        return item

    def close_spider(self, spider):
        self.wb.save('book.xlsx')
        self.wb.close()
'''
#  建好库和表后随便用

import pymysql

class XimaPipeline(object):
    def __init__(self):
        self.conn = pymysql.connect(
            host = "localhost",
            user = "root",
            passwd = "",
            charset = "utf8"
        )

    def process_item(self, item, spider):
        cursor = self.conn.cursor()
        cursor.execute("use xima")
        sql = 'insert into sound(trackid,href) values(%s,%s)'

        if item['href'].isspace() :
            pass
        else:
            cursor.execute(sql,(str(item['id']),item['href']))
            cursor.connection.commit()
        #return item
        pass

    def close_spider(self, spider):
        self.conn.close()
        self.cursor.close()
        
'''


