#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import requests
from requests_html import HTML
import pandas as pd
import re
import urllib.parse
import threading

class BooksCrawler(object):
    def __init__(self):
        self.header = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36"}
        self.domain = 'https://www.books.com.tw/'
        self.key_words = [r'折扣', r'打折', r'優惠', r'特賣', r'特價', r'降價', r'免運']
        self.Life_key_words = [r'']
        self.block_words = [r'特賣會']

    def crawl_books_info(self, boards, df_name):
        board_collected_meta = []
        for board_name in boards:
            start_url = self.domain + board_name + '/index.html'
            num_pages = 300
            board_collected_meta += self.get_paged_meta(start_url, num_pages)
        article_df = pd.DataFrame(board_collected_meta)
        article_df.to_csv(df_name+'.csv')
        # print(article_df)

    def get_metadata_from(self, url):
        pass

    def find_side_category(self, parameter_list):
        pass

    def test(self, url):
        url = urllib.parse.urljoin(self.domain, 'web/books_topm_19/')
        response = requests.get(url, self.header)
        # html = HTML(html=doc)
        print(response.text)

if __name__ == "__main__":
    crawler = BooksCrawler()
    crawler.test(crawler.domain)
    