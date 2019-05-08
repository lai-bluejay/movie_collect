# -*- coding: utf-8 -*-
from urllib.parse import urlparse, parse_qs

import scrapy

from moviecol.items import MoviecolItem


class CommonSpider(scrapy.Spider):
    keys_map = {
        '影片名称: ': 'name',
        '影片别名: ': 'name_alias',
        '影片备注: ': 'note',
        '影片主演: ': 'actors',
        '影片导演: ': 'director',
        '栏目分类: ': 'category',
        '语言分类: ': 'language',
        '影片地区: ': 'region',
        '上映年份: ': 'year',
    }

    extra_info_keys = [
        'name_alias',
        'director',
        'actors',
        'epocs',
        'category',
        'region',
        'language',
        'year',
        'update_times'
    ]

    all_xpath_rules = {
        'base_info': '//div[@class="vodh"]/*/text()',
        'extra_info': '//div[@class="vodinfobox"]/ul/li/span',
        'data_list': "///span[@class='xing_vb4']/a/@href",
        'next_page': '//a[contains(text(), "下一页")]/@href',
        'play_link': "//div[@class='vodplayinfo']/div/ul[1]/li/a/text()",
        'm3u8_link': "//div[@class='vodplayinfo']/div/ul[2]/li/a/text()",
        'cover_img': '//div[@class="vodImg"]/img/@src',
        'synopsis_text': '//div[@class="vodplayinfo"]/text()',
        'video_details': '//div[@class="vodDetail"]/li[@class="sa"]|//div[@class="videoDetail"]/li[not(@class)]/div'
    }

    m3u8_path_regexs = [
        'var main = "([^"]+)"',  # https://videos2.jsyunbf.com/share/goIhGy3xA1hoPfMe
        'var huiid = "([^"]+)"',
    ]

    @staticmethod
    def _generate_start_urls(base_url="https://www.okzyw.com/?m=vod-type-id-{}.html", end_num=20):
        urls = [base_url.format(str(i)) for i in range(end_num+1)]
        return urls

    def _get_episode_link(self, link_selector):
        res_list = list()
        for tmp in link_selector:
            try:
                d = tmp.get().split('$')
                res_list.append({d[0]:d[1]})
            except:
                break
        return res_list

    def parse_film_detail(self, response):
        film = response.meta.get('film', MoviecolItem(source=self.name))
        name, update, score = response.selector.xpath('//div[@class="vodh"]/*/text()')
        film['name'] = name.get()
        film['latest'] = update.get()
        film['score'] = score.get()
        img_src = response.selector.xpath(self.all_xpath_rules['cover_img']).extract_first()
        # film_cover = parse_qs(urlparse(img_src).query)['url'][0]
        film['cover'] = img_src
        extra_info = response.selector.xpath(self.all_xpath_rules['extra_info'])
        tmp_d = dict()
        for i, key in enumerate(self.extra_info_keys):
            try:
                s = extra_info[i].xpath('text()').get().strip()
            except:
                # 无字符串
                s = ''
            tmp_d[key] = s
        film.update(tmp_d)

        synopsis = response.selector.xpath(self.all_xpath_rules['synopsis_text']).extract()
        film['synopsis'] = ''.join(synopsis)  # 影片简介.

        # 一堆剧集的链接， list
        m3u8_link = self._get_episode_link(response.selector.xpath(self.all_xpath_rules['m3u8_link']))
        film['m3u8_url'] = m3u8_link
        
        url = self._get_episode_link(response.selector.xpath(self.all_xpath_rules['play_link']))
        film['url'] = url
        yield film

    def parse_film_m3u8(self, response):
        film = response.meta['film']
        seletor = scrapy.Selector(text=response.text)
        m3u8_path = None
        for regex in self.m3u8_path_regexs:
            m3u8_path = seletor.re_first(regex)
            if m3u8_path:
                break
        if m3u8_path:
            film['url'] = '{host}{path}'.format(host=urlparse(response.url).netloc, path=m3u8_path)
        return film

    def parse(self, response):
        for film_link in response.selector.xpath(self.all_xpath_rules['data_list']).extract():
            yield response.follow(film_link, callback=self.parse_film_detail)
        next_page = response.selector.xpath(self.all_xpath_rules['next_page']).extract_first()
        if next_page:
            yield response.follow(next_page)
