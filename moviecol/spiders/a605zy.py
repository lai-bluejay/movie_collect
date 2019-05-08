# -*- coding: utf-8 -*-
import scrapy

from moviecol.spiders.spider import CommonSpider

class A605zySpider(CommonSpider):
    name = '605zy'
    base_url = 'http://www.605zy.com/vod-type-id-{}-pg-1.html'
    start_urls = CommonSpider._generate_start_urls(base_url, 20)