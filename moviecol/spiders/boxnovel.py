#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
spiders/boxnovel.py was created on 2019/11/21.
file in :relativeFile
Author: Charles_Lai
Email: lai.bluejay@gmail.com
"""
from scrapy.spiders import Spider

class BoxNovelSpider(Spider):
    name = 'boxnovel'
    start_urls = 'https://boxnovel.com/novel/'

    def parse(self, response):
        titles = response.xpath("//div[@class='post-title font-title']//a/text()").extract()
        
        print(titles)
