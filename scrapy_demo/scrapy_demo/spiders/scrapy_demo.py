#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2021/2/1 13:45
# @File : scrapy_demo
import time
import uuid

import scrapy


class DemoSpider(scrapy.Spider):
    name = 'scrapyDemo'
    allowed_domains = ['anjuke.com']
    start_urls = ['https://cd.fang.anjuke.com/loupan/chenghua/w1/']
    # 配置自定义类 PIPELINES
    custom_settings = {'ITEM_PIPELINES': {'scrapy_demo.pipelines.PipelineImages': 1,
                                          'scrapy_demo.pipelines.PipelineMySql': 300}}

    def parse(self, response):
        """ yield item  提交给管道文件处理 pipelines
            yield scrapy.Request( next_url, callback=self.parse)   提交子请求，回调递归处理
            response.urljoin()   拼凑成绝对网址
            scrapy.FormRequest(url=url, formdata=data, callback=self.parse) post请求
            images_urls 是在items.py中配置的网络爬取得图片地址
        """
        results = response.xpath("//div[contains(@class,'key-list')]//div[@class='item-mod ']")
        print(response.url)
        for it in results:
            item = {}
            price = it.xpath(".//a[@class='favor-pos']//text()").extract()
            item['price'] = ''.join([i.strip() for i in price])
            item['title'] = it.xpath(".//span[@class='items-name']//text()").extract_first()
            item['address'] = it.xpath(".//span[@class='list-map']//text()").extract_first()
            types = it.xpath(".//a[@class='huxing']//text()").extract()
            for i, val in enumerate(types):
                types[i] = val.strip()
            product_type = ''.join(types)
            item['product_type'] = product_type
            classified = it.xpath(".//div[@class='tag-panel']//text()").getall()
            item['classified'] = ''.join([i.strip() for i in classified])
            source_site = it.xpath(".//a[@class='lp-name']/@href").get()
            item['source_site'] = source_site
            item['unique_key'] = uuid.uuid1().hex if source_site is None \
                else source_site[source_site.rindex('/') + 1:source_site.rindex('.')]
            item["publish_time"] = item["spider_time"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            item["city"] = item["area"] = None
            item["version"] = 1
            yield scrapy.Request(response.urljoin(item['source_site']), callback=self.detail_page, cb_kwargs=item)
        next_page = response.xpath("//div[@class='pagination']//a[contains(@class,'next-page')]//@href").extract_first()
        if next_page is not None:
            yield scrapy.Request(next_page, callback=self.parse)

    def detail_page(self, response, **kwargs):
        print(response.url)
        print(kwargs)

        yield kwargs
