# -*- coding: utf-8 -*-
import scrapy
from moviecol.spiders.spider import CommonSpider


class OkzywSpider(CommonSpider):
    name = 'okzyw'
    allowed_domains = ['okzyw.com']
    base_url = "https://www.okzyw.com/?m=vod-type-id-{}.html"
    start_urls = CommonSpider._generate_start_urls(base_url, end_num=22)

    all_xpath_rules = {
        'base_info': '//div[@class="vodh"]/*/text()',
        'extra_info': '//div[@class="vodinfobox"]/ul/li/span',
        'data_list': "///span[@class='xing_vb4']/a/@href",
        'next_page': '//a[contains(text(), "下一页")]/@href',
        'play_link': "//div[@class='vodplayinfo']/div/div[@id=1]/ul/li/text()",
        'm3u8_link': '//div[@class="vodplayinfo"]/div/div[@id=2]/ul/li/text()',
        'cover_img': '//div[@class="vodImg"]/img/@src',
        'synopsis_text': '//div[@class="vodplayinfo"]/text()',
        'video_details': '//div[@class="vodDetail"]/li[@class="sa"]|//div[@class="videoDetail"]/li[not(@class)]/div'
    }
