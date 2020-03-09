# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
import json
from ..items import XimaItem
import re
import math
'''
   12分25秒，爬取喜马拉雅有声书数据并初步清洗，最后储存数据总量为60348条数据。
   数据可存本地(book.xlsx)，也可以存MySQL
   可提高性能：用Xpath代替BeautifulSoup   配置自己的下载中间件
'''

headers ={ 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
           'Referer':'https://www.ximalaya.com/'
           }

class XimaspiderSpider(scrapy.Spider):
    name = 'ximaSpider'
    allowed_domains = ['ximalaya.com']
    start_urls = ['http://ximalaya.com/']

    def parse(self, response):
        bs = BeautifulSoup(response.text,'lxml')
        urls = bs.find_all('li',class_='nE_')
        # print(urls)

        for url in urls:
            href = url.find('a',class_='album-title line-1 lg bold _Ht')['href'][1:]
            url_href = self.start_urls[0] + href
        # print(url_href)
            yield scrapy.Request(url_href ,headers = headers ,callback=self.parse_sound)

    """
    # 只爬取第一页数据
    def parse_sound(self,response):
        bs = BeautifulSoup(response.text,'lxml')
        urls = bs.find_all('div',class_='text _Vc')
        # print(urls)

        for url in urls:
            url_id = url.find('a')['href']
            index = url_id.rfind('/')
            url_href= 'https://www.ximalaya.com/revision/play/v1/audio?id={}&ptype=1'.format(url_id[index+1:])
            yield scrapy.Request(url_href,headers = headers,callback=self.parse_media)
            #print(url_href)
    """

    def parse_sound(self, response):
        """

        本函数的目的是爬取特定有声书的所有音频文件的地址。
        这里涉及到了页面的跳转，虽然跳转页面间的URL有规律，但是不同有声书的源码结构有所区别
        具体表现为标签class属性值有的书之间相同，有的书之间不同（挺坏的）
        但是每页最大存放集数是30固定的。所以我爬取每本有声书的总集数，计算出总页数，最后构造每页的URL进行爬取

        """
        bs = BeautifulSoup(response.text, 'lxml')
        pageinfo = bs.find('h2',class_='_Qp').text
        num = re.search(r"\d+\.?\d*", pageinfo)
        pagenum = math.ceil(int(num.group(0))/30)
        href = bs.find_all('ul',class_='pagination-page _Xo')[0].find('a')['href']

        for page in range(1,pagenum):
            urlnew = self.start_urls[0] + href[1:] + 'p'+str(page)
            yield scrapy.Request(urlnew,headers=headers,callback = self.parsenext)


    def parsenext(self,response):
        """
        由于爬取的是音频文件信息，所以要做好信息被加密的准备。
        Chrome F12 Network找到Media文件，分析文件内的数据，文件为json
        发现trackId和音频文件URL有关
        这样就可以提取数据了
        """
        bs = BeautifulSoup(response.text,'lxml')
        urls = bs.find_all('div', class_='text _Vc')
        # print(urls)

        for url in urls:
            url_id = url.find('a')['href']
            index = url_id.rfind('/')
            url_href = 'https://www.ximalaya.com/revision/play/v1/audio?id={}&ptype=1'.format(url_id[index + 1:])
            yield scrapy.Request(url_href, headers=headers, callback=self.parse_media)
            # print(url_href)


    def parse_media(self,response):
        html = response.text
        json_data=json.loads(html)
        item = XimaItem()
        item['href'] = json_data['data']['src']
        item['id'] = json_data['data']['trackId']
        yield item











